from __future__ import annotations

import inspect
import sys
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Collection,
    Mapping,
    Protocol,
    Union,
)

import pyarrow
from _chalk_shared_public.chalk_function_registry import CHALK_SQL_FUNCTION_REGISTRY

from libchalk.chalksql import (
    ChalkSqlCatalog,
    PyTableProvider,
    sql_to_table,
)
from libchalk.chalktable import ChalkTable, SchemaDescriptor

from ._display import format_materialized_table
from .dataframe import DataFrame, _generate_table_name
from .lazyframe import LazyFrame

# TODO: support LazyFrame
COMPATIBLE_TYPES = (pyarrow.Table, pyarrow.RecordBatch, DataFrame)

# Default display limits for interactive SQL sessions
DEFAULT_MAX_DISPLAY_ROWS = 100
DEFAULT_MAX_COL_WIDTH = 50

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping
    from types import TracebackType
    from typing import Any, TypeAlias

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

    CompatibleFrameType: TypeAlias = Union[pyarrow.Table, pyarrow.RecordBatch, DataFrame, LazyFrame]

    from libchalk.chalksql import BatchUDFTableProvider, PyTableProvider
    from libchalk.utils import ChalkError as LibChalkError

    class TableProviderSpec(Protocol):
        def scan(self) -> ChalkTable: ...
        def get_schema(self) -> SchemaDescriptor: ...

    # taken from chalk-private/engine/chalkengine/chalksql/providers
    class SchemaProvider(Protocol):
        """Protocol for schema providers that provide table information and table resolution."""

        def get_tables(self) -> list[str]:
            """Return a list of available table names."""
            ...

        def resolve_table(self, table_name: str) -> "PyTableProvider | BatchUDFTableProvider | LibChalkError":
            """Resolve a table name to a table provider, or a LibChalkError for user errors"""
            ...

        def get_description(self) -> str:
            """Return a description of the schema provider."""
            ...


# implements TableProvider
class SimpleTableProvider:
    def __init__(self, table: ChalkTable):
        self.table = table

    def get_schema(self) -> SchemaDescriptor:
        return self.table.schema

    def scan(self) -> ChalkTable:
        return self.table


# implements SchemaProvider
class SimpleSchemaProvider:
    def __init__(self, tables: dict[str, ChalkTable]):
        self.tables = tables

    def get_tables(self):
        return list(self.tables.keys())

    def register_table(self, name: str, table: ChalkTable):
        self.tables[name] = table

    def resolve_table(self, table_name: str):
        return PyTableProvider(SimpleTableProvider(self.tables[table_name]))

    def get_description(self):
        return "The set of ChalkTable's registered in SQLContext"


def _get_frame_locals(
    *,
    of_type: type | Collection[type] | Callable[[Any], bool] | None = COMPATIBLE_TYPES,
    n_objects: int | None = None,
    named: str | Collection[str] | None = None,
) -> dict[str, Any]:
    """Return compatible frame objects from the local stack."""
    return _get_stack_locals(of_type=of_type, n_objects=n_objects, named=named)


def _get_stack_locals(
    of_type: type | Collection[type] | Callable[[Any], bool] | None = None,
    *,
    named: str | Collection[str] | None = None,
    n_objects: int | None = None,
    n_frames: int | None = None,
) -> dict[str, Any]:
    """
    Taken from: https://github.com/pola-rs/polars/blob/py-1.34.0/py-polars/src/polars/_utils/various.py#L507
    Retrieve f_locals from all (or the last 'n') stack frames from the calling location.

    Parameters
    ----------
    of_type
        Only return objects of this type; can be a single class, tuple of
        classes, or a callable that returns True/False if the object being
        tested is considered a match.
    n_objects
        If specified, return only the most recent `n` matching objects.
    n_frames
        If specified, look at objects in the last `n` stack frames only.
    named
        If specified, only return objects matching the given name(s).
    """
    objects: dict[str, CompatibleFrameType] = {}
    examined_frames = 0

    if isinstance(named, str):
        named = (named,)
    if n_frames is None:
        n_frames = sys.maxsize

    if inspect.isfunction(of_type):
        matches_type = of_type
    else:
        if isinstance(of_type, Collection):
            of_type = tuple(of_type)

        def matches_type(obj: Any) -> bool:
            return isinstance(obj, of_type)  # type: ignore[arg-type]

    if named is not None:
        if isinstance(named, str):
            named = (named,)
        elif not isinstance(named, set):
            named = set(named)

    stack_frame = inspect.currentframe()
    stack_frame = getattr(stack_frame, "f_back", None)
    try:
        while stack_frame and examined_frames < n_frames:
            local_items = list(stack_frame.f_locals.items())
            global_items = list(stack_frame.f_globals.items()) if stack_frame.f_globals else []

            # Search locals first
            for nm, obj in reversed(local_items):
                if nm not in objects and (named is None or nm in named) and (of_type is None or matches_type(obj)):
                    objects[nm] = obj
                    if n_objects is not None and len(objects) >= n_objects:
                        return objects

            # Also check globals for the current frame
            for nm, obj in reversed(global_items):
                if nm not in objects and (named is None or nm in named) and (of_type is None or matches_type(obj)):
                    objects[nm] = obj
                    if n_objects is not None and len(objects) >= n_objects:
                        return objects

            stack_frame = stack_frame.f_back
            examined_frames += 1
    finally:
        # https://docs.python.org/3/library/inspect.html
        # > Though the cycle detector will catch these, destruction of the frames
        # > (and local variables) can be made deterministic by removing the cycle
        # > in a finally clause.
        del stack_frame

    return objects


class SQLContext:
    """
    Run SQL queries against DataFrame and arrow data.
    """

    _catalog: ChalkSqlCatalog
    _env: str
    _schema_prover: SimpleSchemaProvider
    _tables_scope_stack: list[set[str]]

    def __init__(
        self,
        frames: Mapping[str, CompatibleFrameType] | None = None,
        *,
        register_globals: bool | int = False,
        function_registry=CHALK_SQL_FUNCTION_REGISTRY,
        **named_frames: CompatibleFrameType,
    ) -> None:
        """
        Initialize a new `SQLContext`.

        Parameters
        ----------
        frames
            A `{name:frame, ...}` mapping which can include DataFrames *and*
            pyarrow Table and RecordBatch objects.
        register_globals
            Register compatible objects found
            in the globals, automatically mapping their variable name to a table name.
            To register other objects (pandas/pyarrow data) pass them explicitly, or
            call the `execute_global` classmethod. If given an integer then only the
            most recent "n" objects found will be registered.
        **named_frames
            Named eager/lazy frames, provided as kwargs.
        """
        frames = dict(frames or {})
        if register_globals:
            for name, obj in _get_frame_locals().items():
                if name not in frames and name not in named_frames:
                    named_frames[name] = obj

        self._env = _generate_table_name()
        self._schema_provider = SimpleSchemaProvider({})
        self._function_registry = function_registry
        self._catalog = ChalkSqlCatalog(function_registry=function_registry)
        self._catalog.register_schema_provider(self._env, self._schema_provider)

        if frames or named_frames:
            frames.update(named_frames)
            self.register_many(frames)

    @classmethod
    def execute_global(cls, query: str) -> DataFrame:
        """
        Immediately execute a SQL query, automatically registering frame globals.

        Parameters
        ----------
        query
            A valid SQL query string.
        """
        # TODO: constrain by table names in query
        with cls(register_globals=True) as ctx:
            return ctx.execute(query=query)

    def __enter__(self) -> Self:
        """Track currently registered tables on scope entry; supports nested scopes."""
        self._tables_scope_stack = getattr(self, "_tables_scope_stack", [])
        self._tables_scope_stack.append(set(self.tables()))
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    def __repr__(self) -> str:
        n_tables = len(self.tables())
        return f"<SQLContext [tables:{n_tables}] at 0x{id(self):x}>"

    def execute(self, query: str) -> DataFrame:
        """
        Parse the given SQL query and execute it against the registered frame data.

        Parameters
        ----------
        query
            A valid string SQL query.
        """
        plan = sql_to_table(
            self._catalog,
            self._env,
            query,
        )
        return DataFrame(plan, {})

    def register(self, name: str, frame: CompatibleFrameType) -> Self:
        """
        Register a single frame as a table, using the given name.

        Parameters
        ----------
        name
            Name of the table.
        frame
            eager/lazy frame to associate with this table name.

        See Also
        --------
        register_globals
        register_many
        """
        if isinstance(frame, pyarrow.Table):
            self._catalog.register_constant_table(name, frame)
        elif isinstance(frame, pyarrow.RecordBatch):
            # Convert RecordBatch to Table
            # TODO: handle with register_record_batch
            self._catalog.register_constant_table(name, pyarrow.Table.from_batches([frame]))
        elif isinstance(frame, DataFrame):
            _pa = frame._maybe_materialized()
            if _pa:
                self._catalog.register_constant_table(name, _pa)
            else:
                self._schema_provider.register_table(name, frame._plan)
        else:
            raise TypeError(f"{name} has unsupported table type {type(frame)}")

        return self

    def register_globals(self, n: int | None = None) -> Self:
        """
        Register all frames (lazy or eager) found in the current globals scope.

        Automatically maps variable names to table names.

        See Also
        --------
        register
        register_many

        Parameters
        ----------
        n
            Register only the most recent "n" frames.
        """
        frames = _get_frame_locals(n_objects=n)
        return self.register_many(frames=frames)

    def register_many(
        self,
        frames: Mapping[str, CompatibleFrameType] | None = None,
        **named_frames: CompatibleFrameType,
    ) -> Self:
        """
        Register multiple eager/lazy frames as tables, using the associated names.

        Parameters
        ----------
        frames
            A `{name:frame, ...}` mapping.
        **named_frames
            Named eager/lazy frames, provided as kwargs.

        See Also
        --------
        register
        register_globals
        """
        frames = dict(frames or {})
        frames.update(named_frames)
        for name, frame in frames.items():
            self.register(name, frame)
        return self

    def tables(self) -> list[str]:
        """
        Return a list of the registered table names.

        Notes
        -----
        The :meth:`tables` method will return the same values as the
        "SHOW TABLES" SQL statement, but as a list instead of a frame.
        """
        result = self.execute("SHOW TABLES")
        arrow_table = result.to_arrow()
        if arrow_table.num_rows > 0:
            return arrow_table.column("table_name").to_pylist()
        return []

    def _run_and_display_query(
        self,
        query: str,
        show_plan: str | None,
        max_display_rows: int,
    ) -> None:
        # Execute query
        start_time = time.time()
        result = self.execute(query)

        if show_plan:
            if show_plan in ("logical", "all"):
                print("\n=== Logical Plan ===")
                print(result.explain_logical())
                print()
            if show_plan in ("physical", "all"):
                print("\n=== Physical Plan ===")
                print(result.explain_physical())
                print()

        table = result.to_arrow()
        elapsed = time.time() - start_time

        print(format_materialized_table(table, head=max_display_rows // 2, tail=max_display_rows // 2))
        print(f"\n(in {elapsed:.3f}s)")

    def interactive(
        self,
        *,
        show_plan: str | None = None,
        max_display_rows: int = DEFAULT_MAX_DISPLAY_ROWS,
    ) -> None:
        """Start an interactive SQL session.

        Parameters
        ----------
        show_plan
            Plan type to show before executing each query: 'logical', 'physical', or 'all'.
            If None, no plan is shown.
        max_display_rows
            Maximum number of rows to display. If exceeded, shows each half from the top/bottom of the results.
        """
        import glob
        import os.path
        import re
        import readline
        from pathlib import Path

        # Set up readline history
        history_file = Path.home() / ".chalkdf_history"
        try:
            readline.read_history_file(history_file)
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass

        # Compile regex patterns for tab completion
        parquet_pattern = re.compile(r"read_parquet\s*\(\s*'([^']*)$", re.IGNORECASE)
        table_pattern = re.compile(r'(\w+)$|"([^"]*)$')

        function_names = self._function_registry.all_names()
        KEYWORDS = [
            "SELECT * FROM ",
            "WHERE ",
            "LIMIT ",
            "DESCRIBE ",
            "OUTER JOIN ",
            "ORDER BY ",
            "GROUP BY ",
            "read_parquet('",
            "HAVING ",
            "EXISTS(SELECT * FROM ",
            "IN (SELECT ",
            "COUNT(DISTINCT ",
            "COUNT(*)",
        ]

        # Set up tab completion
        def completer(text: str, state: int) -> str | None:
            """Tab completion for table names, function names, and file paths in read_parquet."""
            line_buffer = readline.get_line_buffer()
            # begin_idx = readline.get_begidx()
            # before_cursor = line_buffer[:begin_idx]

            matches: list[str] = []
            prefix = ""

            # Check if we're inside read_parquet('...')
            if parquet_match := parquet_pattern.search(line_buffer):
                prefix = parquet_match.group(1)

                parquets: list[str] = []
                dirs: list[str] = []
                other: list[str] = []
                for m in glob.glob(prefix + "*"):
                    if os.path.isdir(m):
                        dirs.append(m + "/")
                    elif m.endswith(".parquet"):
                        parquets.append(m + "')")
                    else:
                        other.append(m + "')")

                # Prefer .parquet files
                matches = parquets + dirs + other
            # Check if we should complete table names or function names
            elif table_match := table_pattern.search(line_buffer):
                tables = self.tables()

                prefix = (table_match.group(1) or table_match.group(2)).lower()
                matches = [t for t in tables if t.startswith(prefix)]
                matches.extend(f for f in function_names if f.startswith(prefix) and f not in matches)
                matches.extend(k for k in KEYWORDS if k.lower().startswith(prefix) and k not in matches)

            if state >= len(matches):
                return None
            else:
                return text + matches[state][len(prefix) :]

        # Check if we're using libedit (common on macOS) instead of GNU readline
        is_libedit = "libedit" in (readline.__doc__ or "")

        readline.set_completer(completer)
        readline.parse_and_bind("bind ^I rl_complete" if is_libedit else "tab: complete")
        readline.set_completer_delims("'\"/().\n")

        print("ChalkDF SQL Interpreter")
        print("Type 'exit' or 'quit' to exit, 'history' to enable history")
        print()

        query_buffer = []
        last_interrupted_line = None

        while True:
            try:
                try:
                    prompt = "sql> " if not query_buffer else "...> "
                    line = input(prompt).strip()
                    last_interrupted_line = None  # Reset on successful input
                except KeyboardInterrupt:
                    curr_line = readline.get_line_buffer()
                    # Treat as empty if same as last interrupt
                    if curr_line == last_interrupted_line:
                        return
                    if query_buffer or curr_line.strip():
                        query_buffer.clear()
                        last_interrupted_line = curr_line
                        continue
                    else:
                        return

                if not line:
                    continue

                # Handle special commands
                if not query_buffer:
                    if line.strip().lower() in ("exit", "quit"):
                        break
                    if line.strip().lower() == "history":
                        history_file.touch()
                        readline.set_history_length(1000)
                        print(f"History enabled: {history_file}")
                        continue

                # Build multi-line query
                query_buffer.append(line)
                if line.endswith("\\"):
                    continue
                query = "\n".join(query_buffer).replace("\\", "")
                query_buffer.clear()

                self._run_and_display_query(
                    query,
                    show_plan=show_plan,
                    max_display_rows=max_display_rows,
                )

            except EOFError:
                print()
                break
            except Exception:
                import traceback

                traceback.print_exc()
                query_buffer.clear()

        if history_file.exists():
            try:
                readline.write_history_file(history_file)
            except Exception:
                pass


def main() -> None:
    """ChalkDF SQL CLI."""
    import argparse

    from chalkdf.config import compilation_config

    parser = argparse.ArgumentParser(description="ChalkDF SQL CLI")
    parser.add_argument("-c", "--command", help="Execute SQL command and exit")
    parser.add_argument("-i", "--interactive", action="store_true", help="Start interactive session")
    parser.add_argument(
        "-p",
        "--plan",
        nargs="?",
        const="logical",
        choices=["logical", "physical", "all"],
        help="Show query plan (default: logical if flag provided)",
    )
    parser.add_argument(
        "--max-display-rows",
        type=int,
        default=DEFAULT_MAX_DISPLAY_ROWS,
        help=f"Maximum number of rows to display (default: {DEFAULT_MAX_DISPLAY_ROWS})",
    )
    parser.add_argument(
        "--enable-combine-aggregation-optimization",
        action="store_true",
        help="Enable combine aggregation optimization",
    )

    args = parser.parse_args()

    ctx = SQLContext(register_globals=False)

    # Apply compilation config if flags are set
    config_kwargs = {}
    if args.enable_combine_aggregation_optimization:
        config_kwargs["enable_combine_aggregation_optimization"] = True

    with compilation_config(**config_kwargs):
        if args.command:
            ctx._run_and_display_query(
                args.command,
                show_plan=args.plan,
                max_display_rows=args.max_display_rows,
            )
        else:
            # Interactive session (default or explicit -i)
            ctx.interactive(
                show_plan=args.plan,
                max_display_rows=args.max_display_rows,
            )


if __name__ == "__main__":
    main()
