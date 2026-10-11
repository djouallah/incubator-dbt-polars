"""Polars dtypes by name, for config that can only carry a name.

YAML (a seed's `column_types`, a source's `read_options`) holds a type as text,
and Polars rejects text where it wants a dtype: `schema={"a": "String"}` fails
with "'str' is not a Polars data type".
"""

from __future__ import annotations

from typing import Any

from dbt_common.exceptions import DbtRuntimeError

import polars as pl

_POLARS_TYPE_MAP: dict[str, type[pl.DataType]] = {
    # Polars-native names
    "Int8": pl.Int8,
    "Int16": pl.Int16,
    "Int32": pl.Int32,
    "Int64": pl.Int64,
    "UInt8": pl.UInt8,
    "UInt16": pl.UInt16,
    "UInt32": pl.UInt32,
    "UInt64": pl.UInt64,
    "Float32": pl.Float32,
    "Float64": pl.Float64,
    "Boolean": pl.Boolean,
    "Utf8": pl.Utf8,
    "String": pl.Utf8,
    "Categorical": pl.Categorical,
    "Date": pl.Date,
    "Datetime": pl.Datetime,
    "Time": pl.Time,
    "Duration": pl.Duration,
    "Decimal": pl.Decimal,
    "Binary": pl.Binary,
    # SQL aliases (lowercase)
    "int8": pl.Int8,
    "int16": pl.Int16,
    "int32": pl.Int32,
    "int64": pl.Int64,
    "tinyint": pl.Int8,
    "smallint": pl.Int16,
    "integer": pl.Int32,
    "int": pl.Int32,
    "int4": pl.Int32,
    "int2": pl.Int16,
    "bigint": pl.Int64,
    "uint8": pl.UInt8,
    "uint16": pl.UInt16,
    "uint32": pl.UInt32,
    "uint64": pl.UInt64,
    "float4": pl.Float32,
    "real": pl.Float32,
    "float32": pl.Float32,
    "float8": pl.Float64,
    "double": pl.Float64,
    "float64": pl.Float64,
    "float": pl.Float64,
    "double precision": pl.Float64,
    "varchar": pl.Utf8,
    "text": pl.Utf8,
    "string": pl.Utf8,
    "char": pl.Utf8,
    "character varying": pl.Utf8,
    "utf8": pl.Utf8,
    "categorical": pl.Categorical,
    "boolean": pl.Boolean,
    "bool": pl.Boolean,
    "date": pl.Date,
    "timestamp": pl.Datetime,
    "datetime": pl.Datetime,
    "time": pl.Time,
    "duration": pl.Duration,
    "decimal": pl.Decimal,
    "numeric": pl.Decimal,
    "binary": pl.Binary,
}


def resolve_polars_type(type_str: str) -> type[pl.DataType]:
    key = type_str.split("(")[0].strip()
    dtype = _POLARS_TYPE_MAP.get(key) or _POLARS_TYPE_MAP.get(key.lower())
    if dtype is None:
        raise DbtRuntimeError(f"Unknown column type: '{type_str}'")
    return dtype


# The scan arguments whose values are dtypes. `schema` and `schema_overrides` map
# a column to a dtype; `schema_overrides` may also be a list, one per column.
_DTYPE_OPTIONS = ("schema", "schema_overrides", "dtypes")


def resolve_read_option_dtypes(read_options: dict[str, Any]) -> dict[str, Any]:
    """`read_options` with every dtype name under a dtype-valued option resolved
    to its Polars dtype. Values that are already dtypes are left alone."""
    out = dict(read_options)
    for key in _DTYPE_OPTIONS:
        value = out.get(key)
        if isinstance(value, dict):
            out[key] = {
                col: resolve_polars_type(t) if isinstance(t, str) else t
                for col, t in value.items()
            }
        elif isinstance(value, list):
            out[key] = [
                resolve_polars_type(t) if isinstance(t, str) else t for t in value
            ]
    return out
