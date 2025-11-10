"""Tests for the ClickHouse to Python type mapper."""

from chty.typemapper import clickhouse_to_python_type, get_required_imports


def test_integer_types():
    assert clickhouse_to_python_type("Int8") == "int"
    assert clickhouse_to_python_type("Int32") == "int"
    assert clickhouse_to_python_type("Int64") == "int"
    assert clickhouse_to_python_type("UInt32") == "int"


def test_float_types():
    assert clickhouse_to_python_type("Float32") == "float"
    assert clickhouse_to_python_type("Float64") == "float"


def test_string_types():
    assert clickhouse_to_python_type("String") == "str"
    assert clickhouse_to_python_type("FixedString") == "str"


def test_bool_type():
    assert clickhouse_to_python_type("Bool") == "bool"


def test_date_types():
    assert clickhouse_to_python_type("Date") == "date"
    assert clickhouse_to_python_type("Date32") == "date"
    assert clickhouse_to_python_type("DateTime") == "datetime"
    assert clickhouse_to_python_type("DateTime64") == "datetime"


def test_nullable_types():
    assert clickhouse_to_python_type("Nullable(Int32)") == "int | None"
    assert clickhouse_to_python_type("Nullable(String)") == "str | None"
    assert clickhouse_to_python_type("Nullable(Float64)") == "float | None"


def test_array_types():
    assert clickhouse_to_python_type("Array(Int32)") == "list[int]"
    assert clickhouse_to_python_type("Array(String)") == "list[str]"
    assert clickhouse_to_python_type("Array(Float64)") == "list[float]"


def test_nested_array_types():
    assert clickhouse_to_python_type("Array(Array(Int32))") == "list[list[int]]"
    assert clickhouse_to_python_type("Array(Nullable(String))") == "list[str | None]"


def test_map_types():
    assert clickhouse_to_python_type("Map(String, Int32)") == "dict[str, int]"
    assert clickhouse_to_python_type("Map(Int32, String)") == "dict[int, str]"


def test_tuple_types():
    assert clickhouse_to_python_type("Tuple(Int32, String)") == "tuple[int, str]"
    assert (
        clickhouse_to_python_type("Tuple(Int32, String, Float64)")
        == "tuple[int, str, float]"
    )


def test_decimal_types():
    assert clickhouse_to_python_type("Decimal") == "float"
    assert clickhouse_to_python_type("Decimal32") == "float"
    assert clickhouse_to_python_type("Decimal64") == "float"


def test_uuid_type():
    assert clickhouse_to_python_type("UUID") == "str"


def test_unknown_type():
    assert clickhouse_to_python_type("UnknownType") == "Any"


def test_get_required_imports_basic():
    imports = get_required_imports(["int", "str", "bool"])
    assert len(imports) == 0


def test_get_required_imports_date():
    imports = get_required_imports(["date"])
    assert "from datetime import date" in imports


def test_get_required_imports_datetime():
    imports = get_required_imports(["datetime"])
    assert "from datetime import datetime" in imports


def test_get_required_imports_date_and_datetime():
    imports = get_required_imports(["date", "datetime"])
    assert "from datetime import date, datetime" in imports


def test_get_required_imports_any():
    imports = get_required_imports(["Any", "int"])
    assert "from typing import Any" in imports
