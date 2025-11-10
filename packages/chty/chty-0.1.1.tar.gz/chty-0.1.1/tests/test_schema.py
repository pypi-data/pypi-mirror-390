"""Tests for schema introspection.

These are integration tests that require a running ClickHouse instance.
Run with: uv run pytest tests/test_schema.py
"""

import pytest

from chty.schema import get_result_schema

DB_URL = "clickhouse://admin:admin@localhost:8123"


@pytest.fixture
def db_url():
    """ClickHouse connection URL."""
    return DB_URL


def test_simple_query(db_url):
    """Test schema introspection for simple SELECT."""
    query = "SELECT 1 AS num"
    schema = get_result_schema(query, db_url)
    
    assert len(schema) == 1
    assert schema[0][0] == "num"
    assert schema[0][1] == "UInt8"


def test_computed_columns(db_url):
    """Test schema introspection for computed columns."""
    query = "SELECT number * 2 AS doubled FROM system.numbers LIMIT 10"
    schema = get_result_schema(query, db_url)
    
    assert len(schema) == 1
    assert schema[0][0] == "doubled"
    assert schema[0][1] == "UInt64"


def test_with_parameters(db_url):
    """Test schema introspection with parameterized query."""
    query = "SELECT number * {mult:Int32} AS result FROM system.numbers LIMIT 10"
    schema = get_result_schema(query, db_url)
    
    assert len(schema) == 1
    assert schema[0][0] == "result"
    assert schema[0][1] == "UInt64"


def test_multiple_columns(db_url):
    """Test schema introspection with multiple columns."""
    query = """
    SELECT 
        number,
        number * 2 AS doubled,
        toString(number) AS str_num
    FROM system.numbers 
    LIMIT 10
    """
    schema = get_result_schema(query, db_url)
    
    assert len(schema) == 3
    assert schema[0][0] == "number"
    assert schema[0][1] == "UInt64"
    assert schema[1][0] == "doubled"
    assert schema[1][1] == "UInt64"
    assert schema[2][0] == "str_num"
    assert schema[2][1] == "String"


def test_complex_types(db_url):
    """Test schema introspection with complex types."""
    query = """
    SELECT 
        toDateTime('2020-01-01 00:00:00') AS dt,
        toDate('2020-01-01') AS d,
        [1, 2, 3] AS arr,
        map('key', 'value') AS m
    """
    schema = get_result_schema(query, db_url)
    
    assert len(schema) == 4
    assert schema[0][0] == "dt"
    assert "DateTime" in schema[0][1]
    assert schema[1][0] == "d"
    assert "Date" in schema[1][1]
    assert schema[2][0] == "arr"
    assert "Array" in schema[2][1]
    assert schema[3][0] == "m"
    assert "Map" in schema[3][1]


def test_nullable_types(db_url):
    """Test schema introspection with nullable types."""
    query = "SELECT nullIf(number, 0) AS nullable_num FROM system.numbers LIMIT 10"
    schema = get_result_schema(query, db_url)
    
    assert len(schema) == 1
    assert schema[0][0] == "nullable_num"
    assert "Nullable" in schema[0][1] or schema[0][1] == "UInt64"


def test_invalid_db_url():
    """Test error handling for invalid db_url."""
    with pytest.raises(ValueError, match="Invalid db_url scheme"):
        get_result_schema("SELECT 1", "http://localhost")


def test_connection_error():
    """Test error handling for connection failure."""
    bad_url = "clickhouse://admin:admin@nonexistent:9999"
    with pytest.raises(Exception):
        get_result_schema("SELECT 1", bad_url)


def test_invalid_query(db_url):
    """Test error handling for invalid SQL."""
    with pytest.raises(Exception):
        get_result_schema("INVALID SQL SYNTAX", db_url)

