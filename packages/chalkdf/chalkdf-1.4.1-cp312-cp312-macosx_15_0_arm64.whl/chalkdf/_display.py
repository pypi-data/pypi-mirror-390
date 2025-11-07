from __future__ import annotations

import math
import typing

import pyarrow

MaterializedLike = pyarrow.RecordBatch | pyarrow.Table


def normalize_materialized_tables(tables: typing.Mapping[str, MaterializedLike]) -> dict[str, pyarrow.Table]:
    """Convert any RecordBatches into Tables for consistent handling."""

    normalized: dict[str, pyarrow.Table] = {}
    for name, table in tables.items():
        if isinstance(table, pyarrow.RecordBatch):
            normalized[name] = pyarrow.Table.from_batches([table])
        else:
            normalized[name] = table
    return normalized


def format_materialized_table(table: pyarrow.Table, head: int = 3, tail: int = 3) -> str:
    """Return a multiline preview string for a materialized Arrow table."""

    total_rows = table.num_rows
    total_cols = len(table.column_names)
    row_label = "row" if total_rows == 1 else "rows"
    col_label = "column" if total_cols == 1 else "columns"
    lines: list[str] = [f"DataFrame(materialized {total_rows} {row_label} x {total_cols} {col_label})"]

    schema_fields = [f"{field.name} ({field.type})" for field in table.schema]
    if schema_fields:
        lines.append("Schema: " + ", ".join(schema_fields))
    else:
        lines.append("Schema: (no columns)")

    if total_rows == 0:
        lines.append("No rows to display.")
        return "\n".join(lines)

    columns = table.column_names
    if not columns:
        lines.append("Showing all rows:")
        lines.append("(no columns)")
        return "\n".join(lines)

    column_labels = {name: f"{name} ({table.schema.field(i).type})" for i, name in enumerate(columns)}
    widths: dict[str, int] = {name: len(label) for name, label in column_labels.items()}

    if total_rows <= head + tail:
        row_indices = list(range(total_rows))
        preview_prefix = "Showing all rows:"
        include_gap = False
    else:
        row_indices = list(range(head))
        row_indices.extend(range(total_rows - tail, total_rows))
        preview_prefix = f"Showing first {head} rows and last {tail} rows:"
        include_gap = True

    lines.append(preview_prefix)

    preview_table = table.take(pyarrow.array(row_indices)) if row_indices else table.slice(0, 0)
    preview_data = preview_table.to_pydict()
    formatted_data: dict[str, list[str]] = {}
    for name in columns:
        values = [_format_preview_value(v) for v in preview_data.get(name, [])]
        formatted_data[name] = values
        for value in values:
            widths[name] = max(widths[name], len(value))

    header = " | ".join(column_labels[name].ljust(widths[name]) for name in columns)
    separator = "-+-".join("-" * widths[name] for name in columns)
    lines.append(header)
    lines.append(separator)

    split_index = min(head, len(row_indices))
    ellipsis_row = " | ".join("...".ljust(widths[name]) for name in columns)
    for idx in range(len(row_indices)):
        if include_gap and idx == split_index:
            lines.append(ellipsis_row)
        row_parts = [formatted_data[name][idx].ljust(widths[name]) for name in columns]
        lines.append(" | ".join(row_parts))

    if include_gap:
        omitted = total_rows - head - tail
        if omitted > 0:
            lines.append(f"... ({omitted} more rows)")

    return "\n".join(lines)


def format_plan_summary(
    schema_dict: typing.Mapping[str, typing.Any],
    materialized_table_count: int,
) -> str:
    """Return a one-line summary for a logical plan."""

    column_names = list(schema_dict.keys())
    total_cols = len(column_names)
    col_label = "column" if total_cols == 1 else "columns"
    lines = [
        f"DataFrame(plan; {total_cols} {col_label}, {materialized_table_count} materialized table(s))",
    ]
    if column_names:
        preview_fields: list[str] = []
        for name in column_names[:5]:
            field = schema_dict[name]
            dtype = getattr(field, "type", field)
            preview_fields.append(f"{name} ({str(dtype)})")
        preview = ", ".join(preview_fields)
        if total_cols > 5:
            preview += ", ..."
        lines.append(f"Columns: {preview}")
    else:
        lines.append("Columns: (none)")
    return "\n".join(lines)


def _format_preview_value(value: typing.Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        return f"{value:.6g}"
    text = str(value)
    if len(text) > 32:
        return text[:29] + "..."
    return text
