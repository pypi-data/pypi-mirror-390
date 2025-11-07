"""Lightweight DataFrame wrapper around Chalk's execution engine.

The :class:`DataFrame` class constructs query plans backed by ``libchalk`` and
can materialize them into Arrow tables.  It offers a minimal API similar to
other DataFrame libraries while delegating heavy lifting to the underlying
engine.
"""

from __future__ import annotations

import typing
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Dict, TypeAlias

import pyarrow
from frozendict import frozendict

from chalkdf.util import get_unique_item
from libchalk.chalktable import (
    AggExpr,
    ChalkTable,
    CompilationOptions,
    CompiledPlan,
    Expr,
    PlanRunContext,
    SchemaDescriptor,
    SortMethod,
    WindowExpr,
    string_to_join_kind,
    string_to_sort_method,
)
from libchalk.metrics import InMemoryMetricsEventCollector
from libchalk.utils import InMemoryErrorCollector

from ._chalk_import import require_chalk_attrs
from ._display import format_materialized_table, format_plan_summary, normalize_materialized_tables
from .config import CompilationConfig, resolve_config
from .schema import Schema

if TYPE_CHECKING:
    from chalk.features import Underscore
    from chalk.sql._internal.sql_source import BaseSQLSource

    from libchalk.chalksql import ChalkSqlCatalog

    from .sql import CompatibleFrameType


MaterializedTable: TypeAlias = pyarrow.RecordBatch | pyarrow.Table


_empty_table_dict = frozendict()
_UNDERSCORE_CLS = None
_UNDERSCORE_ATTR = None
_UNDERSCORE_ROOT = None
_BASE_SQL_SOURCE_CLS = None


def _get_underscore_cls():
    global _UNDERSCORE_CLS
    if _UNDERSCORE_CLS is None:
        _UNDERSCORE_CLS = require_chalk_attrs("chalk.features", "Underscore")
    return _UNDERSCORE_CLS


def _get_underscore_attr_and_root():
    global _UNDERSCORE_ATTR
    global _UNDERSCORE_ROOT
    if _UNDERSCORE_ATTR is None:
        _UNDERSCORE_ATTR = require_chalk_attrs("chalk.features.underscore", "UnderscoreAttr")
    if _UNDERSCORE_ROOT is None:
        _UNDERSCORE_ROOT = require_chalk_attrs("chalk.features.underscore", "UnderscoreRoot")
    return _UNDERSCORE_ATTR, _UNDERSCORE_ROOT


def _get_base_sql_source_cls():
    global _BASE_SQL_SOURCE_CLS
    if _BASE_SQL_SOURCE_CLS is None:
        _BASE_SQL_SOURCE_CLS = require_chalk_attrs("chalk.sql._internal.sql_source", "BaseSQLSource")
    return _BASE_SQL_SOURCE_CLS


def _generate_table_name(prefix: str = "") -> str:
    """Generate a unique table name with an optional ``prefix``."""

    return prefix + str(uuid.uuid4())


def _process_sort_cols(columns: typing.Sequence[str | tuple[str, str]]) -> list[tuple[str, SortMethod]]:
    sort_cols: list[tuple[str, SortMethod]] = []
    for col in columns:
        if isinstance(col, str):
            sort_cols.append((col, SortMethod.ASCENDING))
        else:
            sort_cols.append((col[0], string_to_sort_method(col[1])))
    return sort_cols


class DataFrame:
    """Logical representation of tabular data.

    A :class:`DataFrame` wraps a :class:`~libchalk.chalktable.ChalkTable`
    plan and a mapping of materialized Arrow tables.  Operations construct new
    plans and return new ``DataFrame`` instances, leaving previous ones
    untouched.
    """

    def __init__(
        self,
        root: ChalkTable | MaterializedTable | dict,
        tables: Dict[str, MaterializedTable] | None = None,
    ):
        """Create a ``DataFrame`` from a plan or materialized Arrow table.

        :param root: Either a ``ChalkTable`` plan or an in-memory Arrow table.
        :param tables: Mapping of additional table names to Arrow data.
        """

        super().__init__()

        self._show_materialized_preview = False
        self._materialized_plan: ChalkTable | None = None

        if isinstance(root, dict):
            root = pyarrow.table(root)
        if isinstance(root, MaterializedTable):
            if isinstance(root, pyarrow.RecordBatch):
                materialized_table = pyarrow.Table.from_batches([root])
            else:
                materialized_table = root
            generated_name = _generate_table_name()
            self._plan: ChalkTable = ChalkTable.named_table(
                generated_name,
                SchemaDescriptor(schema=materialized_table.schema, sorted_by=[], partitioned_by="single_threaded"),
            )
            self._tables = {generated_name: materialized_table}
            self._show_materialized_preview = True
            self._materialized_plan = self._plan
        else:
            self._plan = root
            self._tables = normalize_materialized_tables(tables) if tables else {}
            self._materialized_plan = None
        self._compiled_plan: CompiledPlan | None = None

    def _maybe_materialized(self) -> pyarrow.Table | None:
        if self._materialized_plan is None or self._plan is not self._materialized_plan or len(self._tables) != 1:
            return None

        only_table = get_unique_item(self._tables.values(), "tables")
        if isinstance(only_table, pyarrow.Table):
            return only_table
        return None

    def __repr__(self) -> str:
        table: pyarrow.Table | None = None
        if self._show_materialized_preview:
            table = self._maybe_materialized()
            if table is None and len(self._tables) == 1:
                only_table = get_unique_item(self._tables.values(), "tables")
                if isinstance(only_table, pyarrow.RecordBatch):
                    table = pyarrow.Table.from_batches([only_table])
        if table is not None:
            return format_materialized_table(table)
        return format_plan_summary(self._plan.schema_dict, len(self._tables))

    __str__ = __repr__

    @classmethod
    def named_table(cls, name: str, schema: pyarrow.Schema) -> DataFrame:
        """Create a ``DataFrame`` for a named table.

        :param name: Table identifier.
        :param schema: Arrow schema describing the table.
        :return: DataFrame referencing the named table.
        """

        return cls(
            ChalkTable.named_table(
                name, SchemaDescriptor(schema=schema, sorted_by=[], partitioned_by="single_threaded")
            )
        )

    @classmethod
    def from_arrow(cls, data: MaterializedTable):
        """Construct a ``DataFrame`` from an in-memory Arrow object."""

        return cls(data)

    @classmethod
    def from_dict(cls, data: dict):
        """Construct a ``DataFrame`` from a python dict."""

        return cls(data)

    @classmethod
    def scan(
        cls,
        name: str,
        input_uris: list[str | Path],
        *,
        schema: pyarrow.Schema | None = None,
    ) -> DataFrame:
        """
        Scan files and return a DataFrame. Currently, CSV (with headers) and Parquet are supported.
        :param name: A name to call the table being scanned.
        :param input_uris: List of URIs to scan.
        :param schema: Schema of the data, required for CSV.
        :return: DataFrame
        """
        # Accept filesystem paths or URIs; construct file:// URIs manually for
        # local paths to avoid percent-encoding partition tokens like '='.
        normalized: list[str] = []
        for p in input_uris:
            s = p if isinstance(p, str) else str(p)
            if "://" in s:
                normalized.append(s)
            else:
                abs_path = str(Path(s).resolve())
                if not abs_path.startswith("/"):
                    normalized.append(Path(s).resolve().as_uri())
                else:
                    normalized.append("file://" + abs_path)
        plan = ChalkTable.table_scan(name, normalized, schema)
        return cls(plan, {})

    @classmethod
    def scan_glue_iceberg(
        cls,
        glue_table_name: str,
        schema: typing.Mapping[str, pyarrow.DataType],
        *,
        batch_row_count: int = 1_000,
        aws_catalog_account_id: typing.Optional[str] = None,
        aws_catalog_region: typing.Optional[str] = None,
        aws_role_arn: typing.Optional[str] = None,
        filter_predicate: typing.Optional[Expr] = None,
        parquet_scan_range_column: typing.Optional[str] = None,
        custom_partitions: typing.Optional[dict[str, tuple[typing.Literal["date_trunc(day)"], str]]] = None,
        partition_column: typing.Optional[str] = None,
    ) -> DataFrame:
        """Load data from an AWS Glue Iceberg table.

        :param glue_table_name: Fully qualified ``database.table`` name.
        :param schema: Mapping of column names to Arrow types.
        :param batch_row_count: Number of rows per batch.
        :param aws_catalog_account_id: AWS account hosting the Glue catalog.
        :param aws_catalog_region: Region of the Glue catalog.
        :param aws_role_arn: IAM role to assume for access.
        :param filter_predicate: Optional filter applied during scan.
        :param parquet_scan_range_column: Column used for range-based reads.
        :param custom_partitions: Additional partition definitions.
        :param partition_column: Column name representing partitions.
        :return: DataFrame backed by the Glue table.
        """

        custom_partitions = {} if custom_partitions is None else custom_partitions
        custom_partitions = {
            partition_column: tuple(partition_definition)  # pyright: ignore
            for partition_column, partition_definition in custom_partitions.items()
        }
        filter_predicate = (
            Expr.lit(pyarrow.scalar(True, type=pyarrow.bool_())) if filter_predicate is None else filter_predicate
        )

        plan = ChalkTable.load_glue_table(
            aws_catalog_account_id=aws_catalog_account_id,
            aws_catalog_region=aws_catalog_region,
            aws_role_arn=aws_role_arn,
            table_name=list(glue_table_name.split(".")),
            schema=pyarrow.schema(schema),
            batch_row_count=batch_row_count,
            filter_predicate=filter_predicate,
            parquet_scan_range_column=parquet_scan_range_column or partition_column,
            custom_partitions=custom_partitions or {},
        )

        return cls(plan, {})

    @classmethod
    def from_catalog_table(
        cls,
        table_name: str,
        *,
        catalog: ChalkSqlCatalog,
    ) -> DataFrame:
        """Create a ``DataFrame`` from a Chalk SQL catalog table."""

        plan = ChalkTable.from_catalog_table(
            table_name,
            catalog=catalog,
        )
        return cls(plan, {})

    @classmethod
    def from_sql(
        cls,
        query: str,
        **tables: CompatibleFrameType,
    ) -> DataFrame:
        """Create a ``DataFrame`` from the result of executing a SQL query (DuckDB dialect).

        :param query: SQL query string (DuckDB dialect).
        :param tables: Named tables to use in the query. Can be Arrow Table, RecordBatch, or DataFrame.
        :return: DataFrame containing the query results.
        """
        from .sql import SQLContext

        if tables:
            # Create a SQL context with the provided tables
            with SQLContext(frames=tables) as ctx:
                return ctx.execute(query)
        else:
            # Use execute_global to auto-register frames from the calling scope
            return SQLContext.execute_global(query)

    @classmethod
    def from_datasource(cls, source: BaseSQLSource, query: str, expected_output_schema: pyarrow.Schema):
        """
        Create a DataFrame from the result of querying a SQL source.
        :param source: SQL source to query.
        :param query: SQL query to execute.
        :param expected_output_schema: Output schema of the query result. The datasource's driver is expected
        to convert the native query result to this schema.
        """
        BaseSQLSource = _get_base_sql_source_cls()

        if not isinstance(source, BaseSQLSource):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError(f"source must be a BaseSQLSource, got {source}")
        if not isinstance(expected_output_schema, pyarrow.Schema):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError("expected_output_schema must be a pyarrow.Schema")
        plan = ChalkTable.from_datasource(source, query, expected_output_schema)
        return cls(plan)

    def _apply_function(
        self, new_plan: ChalkTable, additional_tables: typing.Mapping[str, MaterializedTable] = _empty_table_dict
    ) -> DataFrame:
        """Return a new ``DataFrame`` with ``new_plan`` and merged tables."""

        combined_tables = normalize_materialized_tables({**self._tables, **additional_tables})
        return DataFrame(new_plan, combined_tables)

    def _compile(
        self,
        *,
        config: CompilationConfig | None = None,
        recompile: bool = False,
    ) -> CompiledPlan:
        """Compile the current plan if necessary.

        Configuration is resolved from multiple sources in priority order:
        1. Explicit ``config`` parameter (highest priority)
        2. Active :func:`~chalkdf.compilation_config` context manager
        3. Global defaults from :func:`~chalkdf.set_compilation_defaults`
        4. Environment variables (e.g., ``CHALK_USE_VELOX_PARQUET_READER``)
        5. Built-in fallback defaults

        :param config: Explicit compilation configuration (highest priority).
        :param recompile: Force recompilation even if a plan exists.
        :return: CompiledPlan ready for execution.
        """

        if self._compiled_plan is None or recompile:
            # Resolve final configuration from all sources
            resolved_config = resolve_config(config)

            # Convert to CompilationOptions kwargs
            options_kwargs = resolved_config.to_dict()
            options = CompilationOptions(**options_kwargs)

            self._compiled_plan = CompiledPlan("velox", options, [self._plan])
        return self._compiled_plan

    def explain_logical(self) -> str:
        """Return a string representation of the logical plan."""

        return self._compile().explain_logical()

    def explain_physical(self) -> str:
        """Return a string representation of the physical plan."""

        return self._compile().explain_physical()

    def _run_context(self) -> PlanRunContext:
        """Construct a default :class:`PlanRunContext` for execution."""

        return PlanRunContext(
            correlation_id=None,
            environment_id="test",
            deployment_id="test_deployment",
            requester_id="requester_id",
            operation_id="dummy_op",
            execution_timestamp=pyarrow.scalar(datetime.now(timezone.utc), pyarrow.timestamp("us", "UTC")),
            is_online=True,
            max_samples=None,
            observed_at_lower_bound=None,
            observed_at_upper_bound=None,
            customer_metadata={},
            shard_id=0,
            extra_attributes={},
            query_context={},
            error_collector=InMemoryErrorCollector(1000),
            metrics_event_collector=InMemoryMetricsEventCollector(1000),
            chalk_metrics=None,
            batch_reporter=None,
            timeline_trace_writer=None,
            plan_metrics_storage_service=None,
            python_context=None,
        )

    def _execute_to_arrow(self, tables: typing.Mapping[str, MaterializedTable]) -> pyarrow.Table:
        """Execute the plan and collect the result into a single Arrow table."""

        result = (
            self._compile()
            .run(
                self._run_context(),
                {**self._tables, **tables},
                {"__execution_ts__": pyarrow.scalar(datetime.now(timezone.utc), pyarrow.timestamp("us", "UTC"))},
            )
            .result()
        )
        return pyarrow.Table.from_batches(result.batches)

    def _as_agg_expr(self, underscore_or_agg_expression: AggExpr | Underscore) -> AggExpr:
        Underscore = _get_underscore_cls()

        if isinstance(underscore_or_agg_expression, AggExpr):
            return underscore_or_agg_expression
        elif isinstance(underscore_or_agg_expression, Underscore):
            from .underscore_conversion.convert_underscore_to_expr import convert_underscore_to_agg_expr

            return convert_underscore_to_agg_expr(underscore_or_agg_expression, self.get_plan().schema_dict)
        else:
            raise ValueError(f"Expected to receive an AggExpr or Underscore, got {type(underscore_or_agg_expression)}")

    def _as_expr(self, underscore_or_expression: Expr | Underscore) -> Expr:
        Underscore = _get_underscore_cls()

        if isinstance(underscore_or_expression, Expr):
            return underscore_or_expression
        elif isinstance(underscore_or_expression, Underscore):
            from .underscore_conversion.convert_underscore_to_expr import convert_underscore_to_expr

            return convert_underscore_to_expr(underscore_or_expression, self.get_plan().schema_dict)
        else:
            raise ValueError(f"Expected to receive an Expr or Underscore, got {type(underscore_or_expression)}")

    @property
    def column_names(self) -> list[str]:
        """Return a list of the column names on this dataframe"""

        return self.schema.names()

    @property
    def column_dtypes(self) -> list[pyarrow.DataType]:
        """Return a list of column data types on this dataframe"""

        return self.schema.dtypes()

    @property
    def schema(self) -> Schema:
        """Return schema of this dataframe"""

        return Schema(self.get_plan().schema_dict)

    @property
    def num_columns(self) -> int:
        """Return the number of columns on this dataframe"""

        return self.schema.len()

    def get_plan(self) -> ChalkTable:
        """Expose the underlying :class:`ChalkTable` plan."""

        return self._plan

    def get_tables(self) -> dict[str, MaterializedTable]:
        """Return the mapping of materialized tables for this DataFrame."""

        return self._tables

    def with_columns(self, dict: typing.Mapping[str, Expr | Underscore]) -> DataFrame:
        """Add or replace columns based on a mapping of expressions."""

        existing = self._plan.schema_dict
        stuff = {k: Expr.column(k, existing[k]) for k in existing}

        for k, v in dict.items():
            stuff[k] = self._as_expr(v)

        new_plan = self._plan.project(stuff)

        return self._apply_function(new_plan)

    def with_unique_id(self, name: str) -> DataFrame:
        """Add a monotonically increasing unique identifier column."""

        new_plan = self._plan.with_unique_id(name)
        return self._apply_function(new_plan)

    def filter(self, expr: Expr | Underscore) -> DataFrame:
        """Filter rows according to ``expr``."""

        new_plan = self._plan.filter(self._as_expr(expr))
        return self._apply_function(new_plan)

    def slice(self, start: int, length: int | None = None) -> DataFrame:
        """Return a subset of rows starting at ``start`` with optional ``length``."""

        # Can't actually express "no limit" with velox limit/offset, but this'll do.
        if length is None:
            length = (2**63) - 1
        elif length <= 0:
            raise ValueError(
                f"'length' parameter in function 'slice' must be a positive integer if specified, received {length}"
            )
        new_plan = self._plan.limit(length, start)
        return self._apply_function(new_plan)

    def col(self, column: str) -> Underscore:
        """
        Get a column expression from the DataFrame.
        :param column: Column name.
        :return: Column expression (as Underscore).
        """
        return self.column(column)

    def column(self, column: str) -> Underscore:
        """
        Get a column expression from the DataFrame.
        :param column: Column name.
        :return: Column expression (as Underscore).
        """
        if column not in self.column_names:
            raise ValueError(f"Column '{column}' not found in DataFrame")
        UnderscoreAttr, UnderscoreRoot = _get_underscore_attr_and_root()
        return UnderscoreAttr(UnderscoreRoot(), column)

    def project(self, columns: typing.Mapping[str, Expr | Underscore]) -> DataFrame:
        """Project to the provided column expressions."""

        projections = {k: self._as_expr(v) for k, v in columns.items()}
        new_plan = self._plan.project(projections)
        return self._apply_function(new_plan)

    def select(self, *columns: str, strict: bool = True) -> DataFrame:
        """Select existing columns by name."""

        try:
            projections = {
                col: Expr.column(col, self._plan.schema_dict[col])
                for col in columns
                if (col in self.column_names or strict)
            }
        except KeyError as ke:
            raise ValueError(f"Column '{ke.args[0]}' not found in DataFrame")

        new_plan = self._plan.project(projections)
        return self._apply_function(new_plan)

    def drop(self, *columns: str, strict: bool = True) -> DataFrame:
        """Drop existing columns by name."""
        if strict:
            bad_cols = tuple(col for col in columns if col not in self.column_names)
            if len(bad_cols) > 0:
                raise ValueError(f"Column(s) '{', '.join(bad_cols)}' not found in DataFrame")
        return self.select(*(col for col in self.column_names if col not in columns))

    def explode(self, column: str) -> DataFrame:
        """
        Explode a column in the DataFrame.
        :param column: Column name to explode.
        :return: DataFrame with exploded column.
        """
        new_plan = self._plan.explode([column])
        return self._apply_function(new_plan)

    def join(self, other: DataFrame, on: dict[str, str] | typing.Sequence[str], how: str = "inner") -> DataFrame:
        """Join this ``DataFrame`` with another.

        :param other: Right-hand ``DataFrame``.
        :param on: Column names or mapping of left->right join keys.
        :param how: Join type (e.g. ``"inner"`` or ``"left"``).
        :return: Resulting ``DataFrame`` after the join.
        """

        if isinstance(on, dict):
            on_left = list(on.keys())
            on_right = [on[r] for r in on_left]
        else:
            on_right = on_left = list(on)
        new_plan = self._plan.join(
            other._plan, on_left, string_to_join_kind(how), right_keys=on_right, right_suffix=None
        )
        return self._apply_function(new_plan, additional_tables=other._tables)

    def window(
        self,
        by: typing.Sequence[str],
        order_by: typing.Sequence[str | tuple[str, str]],
        *expressions: WindowExpr,
    ) -> DataFrame:
        """Compute windowed expressions 'expressions' over 'by' columns ordered by 'order_by' columns. Overlap in `by` and `order_by` is not allowed"""

        sort_cols = _process_sort_cols([*by, *order_by])
        new_plan = (
            self._plan.partition_by(list(by))
            .sort_by(sort_cols)
            .window(list(expressions), [*by], _process_sort_cols([*order_by]))
        )
        return self._apply_function(new_plan)

    def agg(self, by: typing.Sequence[str], *aggregations: AggExpr | Underscore) -> DataFrame:
        """Group by ``by`` columns and apply aggregation expressions."""

        new_plan = self._plan.aggregate_exprs([*by], [self._as_agg_expr(agg) for agg in aggregations])
        return self._apply_function(new_plan)

    def distinct_on(self, *columns: str) -> DataFrame:
        """Drop rows that have identical values in the ``columns``. The kept row is chosen arbitrarily"""

        if len(columns) == 0:
            raise ValueError("Must specify column(s) to distinct on.")

        return self.agg(
            columns, *[self.column(col).one().alias(col) for col in self.column_names if col not in columns]
        ).project({x: self.col(x) for x in self.column_names})

    def order_by(self, *columns: str | tuple[str, str]) -> DataFrame:
        """Sort the ``DataFrame`` by one or more columns."""

        sort_cols = _process_sort_cols(columns)
        new_plan = self._plan.sort_by(sort_cols)
        return self._apply_function(new_plan)

    def rename(self, new_names: dict[str, str]) -> DataFrame:
        """
        Rename columns in the DataFrame.
        :param new_names: Dictionary mapping old column names to new column names.
        :return: DataFrame with renamed columns.
        """

        for nn in new_names:
            if nn not in self.column_names:
                raise ValueError(f"Column '{nn}' not found in DataFrame")

        return self.project({new_names.get(k, k): self.col(k) for k in self.column_names})

    def to_arrow(self, tables: typing.Mapping[str, MaterializedTable] = _empty_table_dict) -> pyarrow.Table:
        """Materialize the plan (if needed) and return a ``pyarrow.Table``."""

        if not tables:
            existing = self._maybe_materialized()
            if existing is not None:
                return existing
        return self._execute_to_arrow(tables)

    def run(self, tables: typing.Mapping[str, MaterializedTable] = _empty_table_dict) -> DataFrame:
        """Materialize the plan and return a ``DataFrame`` backed by an Arrow table."""

        return DataFrame.from_arrow(self.to_arrow(tables))
