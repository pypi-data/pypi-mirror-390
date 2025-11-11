import warnings
from typing import Dict, List, Literal, NamedTuple, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
from kumoapi.pquery import QueryType, ValidatedPredictiveQuery
from kumoapi.pquery.AST import (
    Aggregation,
    ASTNode,
    Column,
    Condition,
    Filter,
    Join,
    LogicalOperation,
)
from kumoapi.task import TaskType
from kumoapi.typing import AggregationType, DateOffset, Stype

import kumoai.kumolib as kumolib
from kumoai.experimental.rfm.local_graph_store import LocalGraphStore
from kumoai.experimental.rfm.pquery import PQueryPandasExecutor

_coverage_warned = False


class SamplingSpec(NamedTuple):
    edge_type: Tuple[str, str, str]
    hop: int
    start_offset: Optional[DateOffset]
    end_offset: Optional[DateOffset]


class LocalPQueryDriver:
    def __init__(
        self,
        graph_store: LocalGraphStore,
        query: ValidatedPredictiveQuery,
        random_seed: Optional[int] = None,
    ) -> None:
        self._graph_store = graph_store
        self._query = query
        self._random_seed = random_seed
        self._rng = np.random.default_rng(random_seed)

    def _get_candidates(
        self,
        exclude_node: Optional[np.ndarray] = None,
    ) -> np.ndarray:

        if self._query.query_type == QueryType.TEMPORAL:
            assert exclude_node is None

        table_name = self._query.entity_table
        num_nodes = len(self._graph_store.df_dict[table_name])
        mask_dict = self._graph_store.mask_dict

        candidate: np.ndarray

        # Case 1: All nodes are valid and nothing to exclude:
        if exclude_node is None and table_name not in mask_dict:
            candidate = np.arange(num_nodes)

        # Case 2: Not all nodes are valid - lookup valid nodes:
        if exclude_node is None:
            pkey_map = self._graph_store.pkey_map_dict[table_name]
            candidate = pkey_map['arange'].to_numpy().copy()

        # Case 3: Exclude nodes - use a mask to exclude them:
        else:
            mask = np.full((num_nodes, ), fill_value=True, dtype=bool)
            mask[exclude_node] = False
            if table_name in mask_dict:
                mask &= mask_dict[table_name]
            candidate = mask.nonzero()[0]

        self._rng.shuffle(candidate)

        return candidate

    def _filter_candidates_by_time(
        self,
        candidate: np.ndarray,
        anchor_time: pd.Timestamp,
    ) -> np.ndarray:

        entity = self._query.entity_table

        # Filter out entities that do not exist yet in time:
        time_sec = self._graph_store.time_dict.get(entity)
        if time_sec is not None:
            mask = time_sec[candidate] <= (anchor_time.value // (1000**3))
            candidate = candidate[mask]

        # Filter out entities that no longer exist in time:
        end_time_col = self._graph_store.end_time_column_dict.get(entity)
        if end_time_col is not None:
            ser = self._graph_store.df_dict[entity][end_time_col]
            ser = ser.iloc[candidate]
            mask = (anchor_time < ser) | ser.isna().to_numpy()
            candidate = candidate[mask]

        return candidate

    def collect_test(
        self,
        size: int,
        anchor_time: Union[pd.Timestamp, Literal['entity']],
        batch_size: Optional[int] = None,
        max_iterations: int = 20,
        guarantee_train_examples: bool = True,
    ) -> Tuple[np.ndarray, pd.Series, pd.Series]:
        r"""Collects test nodes and their labels used for evaluation.

        Args:
            size: The number of test nodes to collect.
            anchor_time: The anchor time.
            batch_size: How many nodes to process in a single batch.
            max_iterations: The number of steps to run before aborting.
            guarantee_train_examples: Ensures that test examples do not occupy
                the entire set of entity candidates.

        Returns:
            A triplet holding the nodes, timestamps and labels.
        """
        batch_size = size if batch_size is None else batch_size

        candidate = self._get_candidates()

        nodes: List[np.ndarray] = []
        times: List[pd.Series] = []
        ys: List[pd.Series] = []

        reached_end = False
        num_labels = candidate_offset = 0
        for _ in range(max_iterations):
            node = candidate[candidate_offset:candidate_offset + batch_size]

            if isinstance(anchor_time, pd.Timestamp):
                node = self._filter_candidates_by_time(node, anchor_time)
                time = pd.Series(anchor_time).repeat(len(node))
                time = time.astype('datetime64[ns]').reset_index(drop=True)
            else:
                assert anchor_time == 'entity'
                time = self._graph_store.time_dict[self._query.entity_table]
                time = pd.Series(time[node] * 1000**3, dtype='datetime64[ns]')

            y, mask = self(node, time)

            nodes.append(node[mask])
            times.append(time[mask].reset_index(drop=True))
            ys.append(y)

            num_labels += len(y)

            if num_labels > size:
                reached_end = True
                break  # Sufficient number of labels collected. Abort.

            candidate_offset += batch_size
            if candidate_offset >= len(candidate):
                reached_end = True
                break

        if len(nodes) > 1:
            node = np.concatenate(nodes, axis=0)[:size]
            time = pd.concat(times, axis=0).reset_index(drop=True).iloc[:size]
            y = pd.concat(ys, axis=0).reset_index(drop=True).iloc[:size]
        else:
            node = nodes[0][:size]
            time = times[0].iloc[:size]
            y = ys[0].iloc[:size]

        if len(node) == 0:
            raise RuntimeError("Failed to collect any test examples for "
                               "evaluation. Is your predictive query too "
                               "restrictive?")

        global _coverage_warned
        if not _coverage_warned and not reached_end and len(node) < size // 2:
            _coverage_warned = True
            warnings.warn(f"Failed to collect {size:,} test examples within "
                          f"{max_iterations} iterations. To improve coverage, "
                          f"consider increasing the number of PQ iterations "
                          f"using the 'max_pq_iterations' option. This "
                          f"warning will not be shown again in this run.")

        if (guarantee_train_examples
                and self._query.query_type == QueryType.STATIC
                and candidate_offset >= len(candidate)):
            # In case all valid entities are used as test examples, we can no
            # longer find any training example. Fallback to a 50/50 split:
            size = len(node) // 2
            node = node[:size]
            time = time.iloc[:size]
            y = y.iloc[:size]

        return node, time, y

    def collect_train(
        self,
        size: int,
        anchor_time: Union[pd.Timestamp, Literal['entity']],
        exclude_node: Optional[np.ndarray] = None,
        batch_size: Optional[int] = None,
        max_iterations: int = 20,
    ) -> Tuple[np.ndarray, pd.Series, pd.Series]:
        r"""Collects training nodes and their labels.

        Args:
            size: The number of test nodes to collect.
            anchor_time: The anchor time.
            exclude_node: The nodes to exclude for use as in-context examples.
            batch_size: How many nodes to process in a single batch.
            max_iterations: The number of steps to run before aborting.

        Returns:
            A triplet holding the nodes, timestamps and labels.
        """
        batch_size = size if batch_size is None else batch_size

        candidate = self._get_candidates(exclude_node)

        if len(candidate) == 0:
            raise RuntimeError("Failed to generate any context examples "
                               "since not enough entities exist")

        nodes: List[np.ndarray] = []
        times: List[pd.Series] = []
        ys: List[pd.Series] = []

        reached_end = False
        num_labels = candidate_offset = 0
        for _ in range(max_iterations):
            node = candidate[candidate_offset:candidate_offset + batch_size]

            if isinstance(anchor_time, pd.Timestamp):
                node = self._filter_candidates_by_time(node, anchor_time)
                time = pd.Series(anchor_time).repeat(len(node))
                time = time.astype('datetime64[ns]').reset_index(drop=True)
            else:
                assert anchor_time == 'entity'
                time = self._graph_store.time_dict[self._query.entity_table]
                time = pd.Series(time[node] * 1000**3, dtype='datetime64[ns]')

            y, mask = self(node, time)

            nodes.append(node[mask])
            times.append(time[mask].reset_index(drop=True))
            ys.append(y)

            num_labels += len(y)

            if num_labels > size:
                reached_end = True
                break  # Sufficient number of labels collected. Abort.

            candidate_offset += batch_size
            if candidate_offset >= len(candidate):
                # Restart with an earlier anchor time (if applicable).
                if self._query.query_type == QueryType.STATIC:
                    reached_end = True
                    break  # Cannot jump back in time for static PQs. Abort.
                if anchor_time == 'entity':
                    reached_end = True
                    break
                candidate_offset = 0
                time_frame = self._query.target_timeframe.timeframe
                anchor_time = anchor_time - (time_frame *
                                             self._query.num_forecasts)
                if anchor_time < self._graph_store.min_time:
                    reached_end = True
                    break  # No earlier anchor time left. Abort.

        if len(nodes) > 1:
            node = np.concatenate(nodes, axis=0)[:size]
            time = pd.concat(times, axis=0).reset_index(drop=True).iloc[:size]
            y = pd.concat(ys, axis=0).reset_index(drop=True).iloc[:size]
        else:
            node = nodes[0][:size]
            time = times[0].iloc[:size]
            y = ys[0].iloc[:size]

        if len(node) == 0:
            raise ValueError("Failed to collect any context examples. Is your "
                             "predictive query too restrictive?")

        global _coverage_warned
        if not _coverage_warned and not reached_end and len(node) < size // 2:
            _coverage_warned = True
            warnings.warn(f"Failed to collect {size:,} context examples "
                          f"within {max_iterations} iterations. To improve "
                          f"coverage, consider increasing the number of PQ "
                          f"iterations using the 'max_pq_iterations' option. "
                          f"This warning will not be shown again in this run.")

        return node, time, y

    def is_valid(
        self,
        node: np.ndarray,
        anchor_time: Union[pd.Timestamp, Literal['entity']],
        batch_size: int = 10_000,
    ) -> np.ndarray:
        r"""Denotes which nodes are valid for a given anchor time, *e.g.*,
        which nodes fulfill entity filter constraints.

        Args:
            node: The nodes to check for.
            anchor_time: The anchor time.
            batch_size: How many nodes to process in a single batch.

        Returns:
            The mask.
        """
        mask: Optional[np.ndarray] = None

        if isinstance(anchor_time, pd.Timestamp):
            node = self._filter_candidates_by_time(node, anchor_time)
            time = pd.Series(anchor_time).repeat(len(node))
            time = time.astype('datetime64[ns]').reset_index(drop=True)
        else:
            assert anchor_time == 'entity'
            time = self._graph_store.time_dict[self._query.entity_table]
            time = pd.Series(time[node] * 1000**3, dtype='datetime64[ns]')

        if isinstance(self._query.entity_ast, Filter):
            # Mask out via (temporal) entity filter:
            executor = PQueryPandasExecutor()
            masks: List[np.ndarray] = []
            for start in range(0, len(node), batch_size):
                feat_dict, time_dict, batch_dict = self._sample(
                    node[start:start + batch_size],
                    time.iloc[start:start + batch_size],
                )
                _mask = executor.execute_filter(
                    filter=self._query.entity_ast,
                    feat_dict=feat_dict,
                    time_dict=time_dict,
                    batch_dict=batch_dict,
                    anchor_time=time.iloc[start:start + batch_size],
                )[1]
                masks.append(_mask)

            _mask = np.concatenate(masks)
            mask = (mask & _mask) if mask is not None else _mask

        if mask is None:
            mask = np.ones(len(node), dtype=bool)

        return mask

    def _get_sampling_specs(
        self,
        node: ASTNode,
        hop: int,
        seed_table_name: str,
        edge_types: List[Tuple[str, str, str]],
        num_forecasts: int = 1,
    ) -> List[SamplingSpec]:
        if isinstance(node, (Aggregation, Column)):
            if isinstance(node, Column):
                table_name = node.fqn.split('.')[0]
                if seed_table_name == table_name:
                    return []
            else:
                table_name = node._get_target_column_name().split('.')[0]

            target_edge_types = [
                edge_type for edge_type in edge_types if
                edge_type[2] == seed_table_name and edge_type[0] == table_name
            ]
            if len(target_edge_types) != 1:
                raise ValueError(
                    f"Could not find a unique foreign key from table "
                    f"'{seed_table_name}' to '{table_name}'")

            if isinstance(node, Column):
                return [
                    SamplingSpec(
                        edge_type=target_edge_types[0],
                        hop=hop + 1,
                        start_offset=None,
                        end_offset=None,
                    )
                ]
            spec = SamplingSpec(
                edge_type=target_edge_types[0],
                hop=hop + 1,
                start_offset=node.aggr_time_range.start_date_offset,
                end_offset=node.aggr_time_range.end_date_offset *
                num_forecasts,
            )
            return [spec] + self._get_sampling_specs(
                node.target, hop=hop + 1, seed_table_name=table_name,
                edge_types=edge_types, num_forecasts=num_forecasts)
        specs = []
        for child in node.children:
            specs += self._get_sampling_specs(child, hop, seed_table_name,
                                              edge_types, num_forecasts)
        return specs

    def get_sampling_specs(self) -> List[SamplingSpec]:
        edge_types = self._graph_store.edge_types
        specs = self._get_sampling_specs(
            self._query.target_ast, hop=0,
            seed_table_name=self._query.entity_table, edge_types=edge_types,
            num_forecasts=self._query.num_forecasts)
        specs += self._get_sampling_specs(
            self._query.entity_ast, hop=0,
            seed_table_name=self._query.entity_table, edge_types=edge_types)
        if self._query.whatif_ast is not None:
            specs += self._get_sampling_specs(
                self._query.whatif_ast, hop=0,
                seed_table_name=self._query.entity_table,
                edge_types=edge_types)
        # Group specs according to edge type and hop:
        spec_dict: Dict[
            Tuple[Tuple[str, str, str], int],
            Tuple[Optional[DateOffset], Optional[DateOffset]],
        ] = {}
        for spec in specs:
            if (spec.edge_type, spec.hop) not in spec_dict:
                spec_dict[(spec.edge_type, spec.hop)] = (
                    spec.start_offset,
                    spec.end_offset,
                )
            else:
                start_offset, end_offset = spec_dict[(
                    spec.edge_type,
                    spec.hop,
                )]
                spec_dict[(spec.edge_type, spec.hop)] = (
                    min_date_offset(start_offset, spec.start_offset),
                    max_date_offset(end_offset, spec.end_offset),
                )

        return [
            SamplingSpec(edge, hop, start_offset, end_offset)
            for (edge, hop), (start_offset, end_offset) in spec_dict.items()
        ]

    def _sample(
        self,
        node: np.ndarray,
        anchor_time: pd.Series,
    ) -> Tuple[
            Dict[str, pd.DataFrame],
            Dict[str, pd.Series],
            Dict[str, np.ndarray],
    ]:
        r"""Samples a subgraph that contains all relevant information to
        evaluate the predictive query.

        Args:
            node: The nodes to check for.
            anchor_time: The anchor time.

        Returns:
            The feature dictionary, the time column dictionary and the batch
            dictionary.
        """
        specs = self.get_sampling_specs()
        num_hops = max([spec.hop for spec in specs] + [0])
        num_neighbors: Dict[Tuple[str, str, str], list[int]] = {}
        time_offsets: Dict[
            Tuple[str, str, str],
            List[List[Optional[int]]],
        ] = {}
        for spec in specs:
            if spec.end_offset is not None:
                if spec.edge_type not in time_offsets:
                    time_offsets[spec.edge_type] = [[0, 0]
                                                    for _ in range(num_hops)]
                offset: Optional[int] = date_offset_to_seconds(spec.end_offset)
                time_offsets[spec.edge_type][spec.hop - 1][1] = offset
                if spec.start_offset is not None:
                    offset = date_offset_to_seconds(spec.start_offset)
                else:
                    offset = None
                time_offsets[spec.edge_type][spec.hop - 1][0] = offset
            else:
                if spec.edge_type not in num_neighbors:
                    num_neighbors[spec.edge_type] = [0] * num_hops
                num_neighbors[spec.edge_type][spec.hop - 1] = -1

        edge_types = list(num_neighbors.keys()) + list(time_offsets.keys())
        node_types = list(
            set([self._query.entity_table])
            | set(src for src, _, _ in edge_types)
            | set(dst for _, _, dst in edge_types))

        sampler = kumolib.NeighborSampler(
            node_types,
            edge_types,
            {
                '__'.join(edge_type): self._graph_store.colptr_dict[edge_type]
                for edge_type in edge_types
            },
            {
                '__'.join(edge_type): self._graph_store.row_dict[edge_type]
                for edge_type in edge_types
            },
            {
                node_type: time
                for node_type, time in self._graph_store.time_dict.items()
                if node_type in node_types
            },
        )

        anchor_time = anchor_time.astype('datetime64[ns]')
        _, _, node_dict, batch_dict, _, _ = sampler.sample(
            {
                '__'.join(edge_type): np.array(values)
                for edge_type, values in num_neighbors.items()
            },
            {
                '__'.join(edge_type): np.array(values)
                for edge_type, values in time_offsets.items()
            },
            self._query.entity_table,
            node,
            anchor_time.astype(int).to_numpy() // 1000**3,
        )

        feat_dict: Dict[str, pd.DataFrame] = {}
        time_dict: Dict[str, pd.Series] = {}
        column_dict: Dict[str, Set[str]] = {}
        for col in self._query.all_query_columns:
            table_name, col_name = col.split('.')
            if table_name not in column_dict:
                column_dict[table_name] = set()
            if col_name != '*':
                column_dict[table_name].add(col_name)
        time_tables = self.find_time_tables()
        for table_name in set(list(column_dict.keys()) + time_tables):
            df = self._graph_store.df_dict[table_name]
            row_id = node_dict[table_name]
            df = df.iloc[row_id].reset_index(drop=True)
            if table_name in column_dict:
                if len(column_dict[table_name]) == 0:
                    # We are dealing with COUNT(table.*), insert a dummy col
                    # to ensure we don't lose the information on node count
                    feat_dict[table_name] = pd.DataFrame(
                        {'ones': [1] * len(df)})
                else:
                    feat_dict[table_name] = df[list(column_dict[table_name])]
            if table_name in time_tables:
                time_col = self._graph_store.time_column_dict[table_name]
                time_dict[table_name] = df[time_col]

        return feat_dict, time_dict, batch_dict

    def __call__(
        self,
        node: np.ndarray,
        anchor_time: pd.Series,
    ) -> Tuple[pd.Series, np.ndarray]:

        feat_dict, time_dict, batch_dict = self._sample(node, anchor_time)

        y, mask = PQueryPandasExecutor().execute(
            query=self._query,
            feat_dict=feat_dict,
            time_dict=time_dict,
            batch_dict=batch_dict,
            anchor_time=anchor_time,
            num_forecasts=self._query.num_forecasts,
        )

        return y, mask

    def find_time_tables(self) -> List[str]:
        def _find_time_tables(node: ASTNode) -> List[str]:
            time_tables = []
            if isinstance(node, Aggregation):
                time_tables.append(
                    node._get_target_column_name().split('.')[0])
            for child in node.children:
                time_tables += _find_time_tables(child)
            return time_tables

        time_tables = _find_time_tables(
            self._query.target_ast) + _find_time_tables(self._query.entity_ast)
        if self._query.whatif_ast is not None:
            time_tables += _find_time_tables(self._query.whatif_ast)
        return list(set(time_tables))

    @staticmethod
    def get_task_type(
        query: ValidatedPredictiveQuery,
        edge_types: List[Tuple[str, str, str]],
    ) -> TaskType:
        if isinstance(query.target_ast, (Condition, LogicalOperation)):
            return TaskType.BINARY_CLASSIFICATION

        target = query.target_ast
        if isinstance(target, Join):
            target = target.rhs_target
        if isinstance(target, Aggregation):
            if target.aggr == AggregationType.LIST_DISTINCT:
                table_name, col_name = target._get_target_column_name().split(
                    '.')
                target_edge_types = [
                    edge_type for edge_type in edge_types
                    if edge_type[0] == table_name and edge_type[1] == col_name
                ]
                if len(target_edge_types) != 1:
                    raise NotImplementedError(
                        f"Multilabel-classification queries based on "
                        f"'LIST_DISTINCT' are not supported yet. If you "
                        f"planned to write a link prediction query instead, "
                        f"make sure to register '{col_name}' as a "
                        f"foreign key.")
                return TaskType.TEMPORAL_LINK_PREDICTION

            return TaskType.REGRESSION

        assert isinstance(target, Column)

        if target.stype in {Stype.ID, Stype.categorical}:
            return TaskType.MULTICLASS_CLASSIFICATION

        if target.stype in {Stype.numerical}:
            return TaskType.REGRESSION

        raise NotImplementedError("Task type not yet supported")


def date_offset_to_seconds(offset: pd.DateOffset) -> int:
    r"""Convert a :class:`pandas.DateOffset` into a maximum number of
    nanoseconds.

    .. note::
        We are conservative and take months and years as their maximum value.
        Additional values are then dropped in label computation where we know
        the actual dates.
    """
    # Max durations for months and years in nanoseconds:
    MAX_DAYS_IN_MONTH = 31
    MAX_DAYS_IN_YEAR = 366

    # Conversion factors:
    SECONDS_IN_MINUTE = 60
    SECONDS_IN_HOUR = 60 * SECONDS_IN_MINUTE
    SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR

    total_ns = 0
    multiplier = getattr(offset, 'n', 1)  # The multiplier (if present).

    for attr, value in offset.__dict__.items():
        if value is None or value == 0:
            continue
        scaled_value = value * multiplier
        if attr == 'years':
            total_ns += scaled_value * MAX_DAYS_IN_YEAR * SECONDS_IN_DAY
        elif attr == 'months':
            total_ns += scaled_value * MAX_DAYS_IN_MONTH * SECONDS_IN_DAY
        elif attr == 'days':
            total_ns += scaled_value * SECONDS_IN_DAY
        elif attr == 'hours':
            total_ns += scaled_value * SECONDS_IN_HOUR
        elif attr == 'minutes':
            total_ns += scaled_value * SECONDS_IN_MINUTE
        elif attr == 'seconds':
            total_ns += scaled_value

    return total_ns


def min_date_offset(*args: Optional[DateOffset]) -> Optional[DateOffset]:
    if any(arg is None for arg in args):
        return None

    anchor = pd.Timestamp('2000-01-01')
    timestamps = [anchor + arg for arg in args]
    assert len(timestamps) > 0
    argmin = min(range(len(timestamps)), key=lambda i: timestamps[i])
    return args[argmin]


def max_date_offset(*args: DateOffset) -> DateOffset:
    if any(arg is None for arg in args):
        return None

    anchor = pd.Timestamp('2000-01-01')
    timestamps = [anchor + arg for arg in args]
    assert len(timestamps) > 0
    argmax = max(range(len(timestamps)), key=lambda i: timestamps[i])
    return args[argmax]
