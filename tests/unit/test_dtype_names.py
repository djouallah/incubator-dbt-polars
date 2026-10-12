import polars as pl
import pytest
from dbt_common.exceptions import DbtRuntimeError

from dbt.adapters.polars.types import resolve_polars_type, resolve_read_option_dtypes


@pytest.mark.parametrize(
    ("name", "dtype"),
    [
        ("String", pl.Utf8),
        ("Int64", pl.Int64),
        ("double", pl.Float64),
        ("varchar", pl.Utf8),
        ("Decimal(18, 2)", pl.Decimal),
    ],
)
def test_resolve_polars_type(name, dtype):
    assert resolve_polars_type(name) == dtype


def test_resolve_polars_type_rejects_unknown():
    with pytest.raises(DbtRuntimeError):
        resolve_polars_type("nope")


def test_schema_names_become_dtypes():
    out = resolve_read_option_dtypes(
        {"has_header": False, "schema": {"a": "Int64", "b": "String"}}
    )
    assert out == {"has_header": False, "schema": {"a": pl.Int64, "b": pl.Utf8}}


def test_schema_overrides_list_and_existing_dtypes():
    out = resolve_read_option_dtypes({"schema_overrides": ["Float64", pl.Int32]})
    assert out == {"schema_overrides": [pl.Float64, pl.Int32]}


def test_other_options_untouched():
    options = {"separator": ";", "infer_schema": False}
    assert resolve_read_option_dtypes(options) == options
