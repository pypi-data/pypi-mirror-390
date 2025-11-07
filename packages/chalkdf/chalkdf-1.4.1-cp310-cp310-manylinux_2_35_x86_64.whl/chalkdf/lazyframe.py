from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Type, cast

import pyarrow as _pa

from chalkdf._chalk_import import require_chalk_attrs, require_chalk_module
from chalkdf.dataframe import DataFrame
from libchalk.chalksql import ChalkSqlCatalog
from libchalk.chalktable import ChalkTable, Expr

_EXPR_PB: Optional[Any] = None
_PRIMITIVE_FEATURE_CONVERTER: Optional[Any] = None
_GRPC_CLIENT_CLS: Optional[type] = None
_UNDERSCORE_CLS: Optional[Any] = None

_SCHEMA_LITERAL_TYPE_KEY = "__lazyframe_literal_type__"
_SCHEMA_LITERAL_SCHEMA_VALUE = "pyarrow_schema"
_SCHEMA_LITERAL_BYTES_KEY = "serialized_schema"


def _get_expr_pb():
    global _EXPR_PB
    if _EXPR_PB is None:
        _EXPR_PB = require_chalk_module("chalk._gen.chalk.expression.v1.expression_pb2")
    return _EXPR_PB


def _get_primitive_feature_converter():
    global _PRIMITIVE_FEATURE_CONVERTER
    if _PRIMITIVE_FEATURE_CONVERTER is None:
        _PRIMITIVE_FEATURE_CONVERTER = require_chalk_attrs(
            "chalk.features._encoding.converter", "PrimitiveFeatureConverter"
        )
    return _PRIMITIVE_FEATURE_CONVERTER


def _get_underscore_cls():
    global _UNDERSCORE_CLS
    if _UNDERSCORE_CLS is None:
        _UNDERSCORE_CLS = require_chalk_attrs("chalk.features", "Underscore")
    return _UNDERSCORE_CLS


def _schema_to_literal_payload(schema: _pa.Schema) -> dict[str, Any]:
    return {
        _SCHEMA_LITERAL_TYPE_KEY: _SCHEMA_LITERAL_SCHEMA_VALUE,
        _SCHEMA_LITERAL_BYTES_KEY: schema.serialize().to_pybytes(),
    }


def _maybe_schema_from_literal_payload(obj: Mapping[str, Any]) -> _pa.Schema | None:
    if obj.get(_SCHEMA_LITERAL_TYPE_KEY) != _SCHEMA_LITERAL_SCHEMA_VALUE:
        return None

    serialized = obj.get(_SCHEMA_LITERAL_BYTES_KEY)
    if isinstance(serialized, _pa.Buffer):
        buffer = serialized
    elif isinstance(serialized, (bytes, bytearray, memoryview)):
        buffer = _pa.py_buffer(serialized)
    else:
        raise ValueError("Serialized schema payload must be bytes-like.")

    return _pa.ipc.read_schema(_pa.BufferReader(buffer))


if TYPE_CHECKING:
    from chalk._gen.chalk.expression.v1 import expression_pb2 as expr_pb
    from chalk.client.client_grpc import ChalkGRPCClient


# Custom stack container with Expr-aware equality for proper stack comparisons
class _LazyFrameStack(list):
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, _LazyFrameStack):
            return NotImplemented
        if len(self) != len(other):
            return False

        def _compare_element(a1: Any, a2: Any):
            if isinstance(a1, list):
                if isinstance(a2, list):
                    for a1_element, a2_element in zip(a1, a2):
                        if not _compare_element(a1_element, a2_element):
                            return False
                    return True
                else:
                    return False

            if isinstance(a1, dict):
                if isinstance(a2, dict):
                    if a1.keys() != a2.keys():
                        return False
                    for key in a1:
                        if not _compare_element(a1[key], a2[key]):
                            return False
                    return True
                else:
                    return False

            if isinstance(a1, Expr) and isinstance(a2, Expr):
                if not a1._structure_equals(a2):
                    return False
                return True
            elif isinstance(a1, Expr) or isinstance(a2, Expr):
                # types mismatch, but we cant coerce to bool so we need to
                # explicitly handle it
                return False
            else:
                return a1 == a2

        # compare each function call
        for (args1, kwargs1), (args2, kwargs2) in zip(self, other):
            if len(args1) != len(args2):
                return False

            # compare args to ensure they match
            for a1, a2 in zip(args1, args2):
                if not _compare_element(a1, a2):
                    return False

            # compare kwargs with short circuiting
            if kwargs1.keys() != kwargs2.keys():
                return False
            for key in kwargs1:
                if not _compare_element(kwargs1[key], kwargs2[key]):
                    return False
        return True


class LazyFrameM(type):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the LazyFrameM instance.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        super().__init__(*args, **kwargs)
        # print("LazyFrameM initialized with args:", args, "and kwargs:", kwargs)

    def __getattr__(self, item: str) -> Any:
        df = LazyFrame()
        return getattr(df, item)


class LazyFrame(metaclass=LazyFrameM):
    """
    A class representing a lazy DataFrame.

    This class is a placeholder for a lazy DataFrame implementation.
    It currently does not contain any methods or attributes.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the LazyFrame instance.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        super().__init__()

        self.stack: _LazyFrameStack = _LazyFrameStack()

    def __getattr__(self, item: str) -> Callable[..., LazyFrame]:
        def proxy(
            *args: Any,
            **kwargs: Any,
        ) -> LazyFrame:
            """
            Proxy method to handle attribute access.

            Args:
                *args: Positional arguments.
                **kwargs: Keyword arguments.
            """
            kwargs["_function_name"] = item
            self._push_call(*args, **kwargs)
            return self

        return proxy

    def _push_call(self, *args: Any, **kwargs: Any) -> None:
        """
        Push a call onto the stack.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """

        if "_function_name" not in kwargs:
            raise ValueError("_function_name is required in kwargs")

        self.stack.append((args, kwargs))

    def run(self, client: ChalkGRPCClient) -> _pa.RecordBatch:
        res = client.execute_plan(lazy_frame_calls=self.to_proto())
        if res.errors:
            raise ValueError(res.errors)
        buffer = _pa.py_buffer(res.feather)
        reader = _pa.ipc.open_stream(buffer)
        return reader.read_next_batch()

    def _convert_to_df(self, catalog: ChalkSqlCatalog | None = None) -> DataFrame:
        el = DataFrame

        def _materialize(value: Any) -> Any:
            if isinstance(value, LazyFrame):
                return value._convert_to_df(catalog=catalog)
            if isinstance(value, tuple):
                return tuple(_materialize(item) for item in value)
            if isinstance(value, list):
                return [_materialize(item) for item in value]
            if isinstance(value, dict):
                return {k: _materialize(v) for k, v in value.items()}
            return value

        for head in self.stack:
            pos_args = head[0]
            kwargs = dict(head[1])
            if (fn := kwargs.get("_function_name", None)) is None:
                raise ValueError("_function_name is required in kwargs")

            del kwargs["_function_name"]
            pos_args = tuple(_materialize(arg) for arg in pos_args)
            kwargs = {k: _materialize(v) for k, v in kwargs.items()}
            if not hasattr(el, fn):
                raise ValueError(f"{fn} is not a valid function in {el.__name__}")
            if fn == "from_catalog_table":
                if catalog is None:
                    raise ValueError("catalog is required to use `from_catalog_table`, none was provided")
                kwargs["catalog"] = catalog
            el = getattr(el, fn)(
                *pos_args,
                **kwargs,
            )
        return cast(DataFrame, el)

    def _prepare_calls_for_proto(
        self, *, catalog: ChalkSqlCatalog | None
    ) -> list[tuple[tuple[Any, ...], dict[str, Any]]]:
        current_df: DataFrame | None = None
        prepared: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

        for args, kwargs in self.stack:
            fn = kwargs.get("_function_name")
            if fn is None:
                raise ValueError("_function_name missing for LazyFrame stack entry")

            raw_kwargs = {k: v for k, v in kwargs.items() if k != "_function_name"}
            raw_args = tuple(args)

            if current_df is not None:
                schema: Mapping[str, _pa.DataType] = current_df.get_plan().schema_dict
                args_prepared = self._maybe_convert_call_args(fn, raw_args, schema)
                kwargs_prepared = self._maybe_convert_call_kwargs(fn, raw_kwargs, schema)
            else:
                args_prepared = raw_args
                kwargs_prepared = raw_kwargs

            prepared.append((args_prepared, {**kwargs_prepared, "_function_name": fn}))

            eval_args = args_prepared if current_df is not None else raw_args
            eval_kwargs = dict(kwargs_prepared if current_df is not None else raw_kwargs)

            if current_df is None:
                eval_target: Callable[..., Any] | None = getattr(DataFrame, fn, None)
            else:
                eval_target = getattr(current_df, fn, None)

            if eval_target is None:
                continue

            if fn == "from_catalog_table" and "catalog" not in eval_kwargs:
                if catalog is None:
                    # Cannot evaluate without catalog; skip schema propagation.
                    continue
                eval_kwargs["catalog"] = catalog

            eval_args = tuple(self._replace_lazyframes(arg, catalog) for arg in eval_args)
            eval_kwargs = {k: self._replace_lazyframes(v, catalog) for k, v in eval_kwargs.items()}

            try:
                result = eval_target(*eval_args, **eval_kwargs)
            except Exception:
                continue
            else:
                if isinstance(result, DataFrame):
                    current_df = result

        return prepared

    def _maybe_convert_call_args(
        self, fn: str, args: tuple[Any, ...], schema: Mapping[str, _pa.DataType]
    ) -> tuple[Any, ...]:
        if not args:
            return tuple()
        if fn in {"with_columns", "project"}:
            return tuple(self._convert_expr_tree(arg, schema) for arg in args)
        if fn == "filter":
            converted = [self._convert_expr_tree(args[0], schema)]
            converted.extend(args[1:])
            return tuple(converted)
        return args

    def _maybe_convert_call_kwargs(
        self, fn: str, kwargs: dict[str, Any], schema: Mapping[str, _pa.DataType]
    ) -> dict[str, Any]:
        if not kwargs:
            return {}
        if fn in {"with_columns", "project"}:
            return {k: self._convert_expr_tree(v, schema) for k, v in kwargs.items()}
        if fn == "filter":
            return {k: self._convert_expr_tree(v, schema) if k == "expr" else v for k, v in kwargs.items()}
        return dict(kwargs)

    def _convert_expr_tree(self, value: Any, schema: Mapping[str, _pa.DataType]) -> Any:
        Underscore = _get_underscore_cls()

        if isinstance(value, Expr):
            return value
        if isinstance(value, LazyFrame):
            return value
        if Underscore is not None and isinstance(value, Underscore):
            from .underscore_conversion.convert_underscore_to_expr import convert_underscore_to_expr

            return convert_underscore_to_expr(value, schema)
        if isinstance(value, list):
            return [self._convert_expr_tree(v, schema) for v in value]
        if isinstance(value, tuple):
            return tuple(self._convert_expr_tree(v, schema) for v in value)
        if isinstance(value, dict):
            return {k: self._convert_expr_tree(v, schema) for k, v in value.items()}
        return value

    def _replace_lazyframes(self, value: Any, catalog: ChalkSqlCatalog | None) -> Any:
        if isinstance(value, LazyFrame):
            return value._convert_to_df(catalog=catalog)
        if isinstance(value, list):
            return [self._replace_lazyframes(v, catalog) for v in value]
        if isinstance(value, tuple):
            return tuple(self._replace_lazyframes(v, catalog) for v in value)
        if isinstance(value, dict):
            return {k: self._replace_lazyframes(v, catalog) for k, v in value.items()}
        return value

    def to_proto(self, *, catalog: ChalkSqlCatalog | None = None) -> expr_pb.LogicalExprNode:
        """
        Convert this LazyFrame's call stack into a nested LogicalExprNode proto.

        Each entry in the stack becomes an ExprCall, chained via get_attribute on the previous node.
        Provide `catalog` when using `from_catalog_table` and underscore expressions so we can resolve schema.
        """
        expr_pb = _get_expr_pb()
        PrimitiveFeatureConverter = _get_primitive_feature_converter()
        prepared_calls = self._prepare_calls_for_proto(catalog=catalog)

        # Helper to wrap a Python/pyarrow value into a literal LogicalExprNode
        def _val_to_node(val: Any) -> expr_pb.LogicalExprNode:
            # LazyFrame nested as argument: embed its full proto
            if isinstance(val, LazyFrame):
                return val.to_proto(catalog=catalog)

            # pyarrow.RecordBatch or Table -> list of struct arrow ScalarValue literal
            if isinstance(val, (_pa.RecordBatch, _pa.Table)):
                rows = val.to_pylist()
                pa_scalar = _pa.scalar(rows)
                pb_scalar = PrimitiveFeatureConverter.from_pyarrow_to_protobuf(pa_scalar)
                lit = expr_pb.ExprLiteral(value=pb_scalar, is_arrow_scalar_object=True)
                return expr_pb.LogicalExprNode(literal_value=lit)

            if isinstance(val, _pa.Schema):
                schema_payload = _schema_to_literal_payload(val)
                return _val_to_node(schema_payload)

            # assume the keys are strings and the values need to be converted
            if isinstance(val, dict):
                converted_values = {k: _val_to_node(v) for k, v in val.items()}
                return expr_pb.LogicalExprNode(
                    call=expr_pb.ExprCall(
                        func=expr_pb.LogicalExprNode(identifier=expr_pb.Identifier(name="dict")),
                        kwargs=converted_values,
                    )
                )

            if isinstance(val, Expr):
                return expr_pb.LogicalExprNode.FromString(val.to_proto_bytes())

            # Primitive or pyarrow.Scalar -> arrow ScalarValue literal
            try:
                is_arrow = isinstance(val, _pa.Scalar)
                pa_scalar = val if is_arrow else _pa.scalar(val)
                pb_scalar = PrimitiveFeatureConverter.from_pyarrow_to_protobuf(pa_scalar)
                lit = expr_pb.ExprLiteral(value=pb_scalar, is_arrow_scalar_object=is_arrow)
                return expr_pb.LogicalExprNode(literal_value=lit)
            except Exception:
                raise ValueError(f"Cannot convert argument to proto literal: {val!r}")

        node: expr_pb.LogicalExprNode | None = None
        # iterate through recorded calls in order
        for args, kwargs in prepared_calls:
            fn = kwargs.get("_function_name")
            # copy kwargs except internal marker
            kw = {k: v for k, v in kwargs.items() if k != "_function_name"}
            # build argument protos
            args_nodes = [_val_to_node(a) for a in args]
            kwargs_nodes = {k: _val_to_node(v) for k, v in kw.items()}

            # prepare the function expression: method call on previous node or base frame
            parent = node or expr_pb.LogicalExprNode(identifier=expr_pb.Identifier(name="chalk_data_frame"))
            get_attr = expr_pb.ExprGetAttribute(parent=parent, attribute=expr_pb.Identifier(name=fn))
            func_node = expr_pb.LogicalExprNode(get_attribute=get_attr)

            # build this call node
            call_node = expr_pb.ExprCall(func=func_node, args=args_nodes, kwargs=kwargs_nodes)
            node = expr_pb.LogicalExprNode(call=call_node)

        # if no calls, return bare frame identifier
        return node or expr_pb.LogicalExprNode(identifier=expr_pb.Identifier(name="chalk_data_frame"))

    def _to_proto(self):
        return self.to_proto()

    @classmethod
    def from_proto_str(cls: Type[LazyFrame], node_bytes: bytes) -> LazyFrame:
        expr_pb = _get_expr_pb()

        return cls.from_proto(expr_pb.LogicalExprNode.FromString(node_bytes))

    @classmethod
    def from_proto(cls: Type[LazyFrame], node: expr_pb.LogicalExprNode) -> LazyFrame:
        """
        Reconstruct a LazyFrame from its LogicalExprNode proto created by to_proto().

        Traverses nested ExprCall/get_attribute to repopulate the call stack.
        """
        PrimitiveFeatureConverter = _get_primitive_feature_converter()

        # Helper to extract Python/pyarrow value from a literal node
        def _node_to_val(n: expr_pb.LogicalExprNode) -> Any:
            if n.HasField("literal_value"):
                lit = n.literal_value
                pa_scalar = PrimitiveFeatureConverter.from_protobuf_to_pyarrow(lit.value)
                if lit.is_arrow_scalar_object:
                    try:
                        if (
                            _pa.types.is_list(pa_scalar.type)
                            and _pa.types.is_struct(pa_scalar.type.value_type)
                            and isinstance(pa_scalar.as_py(), list)
                        ):
                            return _pa.Table.from_pylist(pa_scalar.as_py())
                    except Exception:
                        pass
                    return pa_scalar
                return pa_scalar.as_py()

            # dict literal nodes -> Python dict
            if n.HasField("call") and n.call.func.HasField("identifier") and n.call.func.identifier.name == "dict":
                dict_value = {k: _node_to_val(v) for k, v in n.call.kwargs.items()}
                schema_value = _maybe_schema_from_literal_payload(dict_value)
                if schema_value is not None:
                    return schema_value
                return dict_value

            # Expr literal/logical nodes -> libchalk Expr
            try:
                return Expr.from_proto(n)
            except Exception:
                pass

            # nested LazyFrame calls
            if n.HasField("call") or n.HasField("get_attribute"):
                return cls.from_proto(n)

            raise ValueError(f"Unsupported literal node for LazyFrame.from_proto: {n}")

        lf = cls()
        # collect (args, kwargs, fn) entries in reverse order
        calls: list[tuple[tuple[Any, ...], dict[str, Any], str]] = []
        cur = node
        # unwind nested calls
        while True:
            if cur.HasField("call"):
                call = cur.call
                fn = None
                func = call.func
                if func.HasField("get_attribute"):
                    fn = func.get_attribute.attribute.name
                    parent = func.get_attribute.parent
                elif func.HasField("identifier"):
                    name = func.identifier.name
                    if name == "chalk_data_frame":
                        # reached base, stop unwinding
                        break
                    fn = name
                    parent = None
                else:
                    break

                # decode args/kwargs
                args = tuple(_node_to_val(a) for a in call.args)
                kwargs = {k: _node_to_val(v) for k, v in call.kwargs.items()}
                calls.append((args, kwargs, fn))
                # move up to parent for next iteration
                if func.HasField("get_attribute") and parent is not None:
                    cur = parent
                    continue
            break

        # rebuild stack in original order
        for args, kwargs, fn in reversed(calls):
            kwargs = {**kwargs, "_function_name": fn}
            lf.stack.append((args, kwargs))
        return lf

    @classmethod
    def plan_from_proto_str(cls: Type[LazyFrame], node_bytes: bytes, catalog: ChalkSqlCatalog | None) -> ChalkTable:
        expr_pb = _get_expr_pb()

        return cls.plan_from_proto(expr_pb.LogicalExprNode.FromString(node_bytes), catalog=catalog)

    @classmethod
    def plan_from_proto(
        cls: Type[LazyFrame], node: expr_pb.LogicalExprNode, catalog: ChalkSqlCatalog | None = None
    ) -> ChalkTable:
        expr_pb = _get_expr_pb()

        if not isinstance(node, expr_pb.LogicalExprNode):
            raise TypeError(
                "LazyFrame.from_proto expects an instance of "
                "`chalk._gen.chalk.expression.v1.expression_pb2.LogicalExprNode`."
            )
        lazy_frame = LazyFrame.from_proto(node)
        df = lazy_frame._convert_to_df(catalog=catalog)
        res = df.get_plan()
        return res

    def __repr__(self) -> str:
        if not self.stack:
            return "LazyFrame()"
        lines: list[str] = ["LazyFrame(", "    chalk_data_frame"]
        for args, kwargs in self.stack:
            fn = kwargs.get("_function_name")
            kw = {k: v for k, v in kwargs.items() if k != "_function_name"}
            args_repr = ", ".join(repr(a) for a in args)
            kwargs_repr = ", ".join(f"{k}={v!r}" for k, v in kw.items())
            all_args = ", ".join(x for x in (args_repr, kwargs_repr) if x)
            lines.append(f"    .{fn}({all_args})")
        lines.append(")")
        return "\n".join(lines)

    __str__ = __repr__

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, LazyFrame):
            return NotImplemented

        return self.stack == other.stack
