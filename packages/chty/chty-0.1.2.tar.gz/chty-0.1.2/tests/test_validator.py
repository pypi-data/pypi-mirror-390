"""Tests for validator module."""

from textwrap import dedent

import pytest

from chty.validator import (
    extract_query_from_file,
    extract_expected_schema,
    extract_expected_parameters,
    validate_file,
    ValidationError,
)


def test_extract_query_from_file(tmp_path):
    """Test extracting QUERY constant from a generated file."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestResult(TypedDict):
                id: int
            
            QUERY = """SELECT id FROM test WHERE id = {id:Int32}"""
            
            class TestQuery:
                pass
        ''').strip()
    )

    query = extract_query_from_file(test_file)
    assert query == "SELECT id FROM test WHERE id = {id:Int32}"


def test_extract_query_missing(tmp_path):
    """Test error when QUERY is missing."""
    test_file = tmp_path / "test.py"
    test_file.write_text("# No query here")

    with pytest.raises(ValidationError, match="Could not find QUERY"):
        extract_query_from_file(test_file)


def test_extract_expected_schema(tmp_path):
    """Test extracting expected schema from TypedDict."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestResult(TypedDict):
                id: int
                name: str
                count: int | None
            
            QUERY = """SELECT id, name, count FROM test"""
        ''').strip()
    )

    schema = extract_expected_schema(test_file)
    assert schema == {
        "id": "int",
        "name": "str",
        "count": "int | None",
    }


def test_extract_expected_schema_no_result(tmp_path):
    """Test extracting schema when no Result TypedDict exists."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import Dict, Any
            
            class TestParams(Dict[str, Any]):
                pass
            
            QUERY = """SELECT id FROM test"""
        ''').strip()
    )

    schema = extract_expected_schema(test_file)
    assert schema == {}


def test_validate_file_valid(tmp_path):
    """Test validation with matching schema."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestResult(TypedDict):
                number: int
            
            QUERY = """SELECT number FROM system.numbers LIMIT 1"""
        ''').strip()
    )

    is_valid, errors = validate_file(
        test_file, "clickhouse://admin:admin@localhost:8123"
    )
    assert is_valid
    assert errors == []


def test_validate_file_no_schema(tmp_path):
    """Test validation when file has no result schema."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import Dict, Any
            
            class TestParams(Dict[str, Any]):
                pass
            
            QUERY = """SELECT 1"""
        ''').strip()
    )

    is_valid, errors = validate_file(
        test_file, "clickhouse://admin:admin@localhost:8123"
    )
    assert not is_valid
    assert any("No result schema found" in err for err in errors)


def test_validate_file_type_mismatch(tmp_path):
    """Test validation with type mismatch."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestResult(TypedDict):
                number: str
            
            QUERY = """SELECT number FROM system.numbers LIMIT 1"""
        ''').strip()
    )

    is_valid, errors = validate_file(
        test_file, "clickhouse://admin:admin@localhost:8123"
    )
    assert not is_valid
    assert any("Result type mismatch" in err for err in errors)
    assert any(
        "query returns int" in err and "generated result expects str" in err
        for err in errors
    )


def test_validate_file_missing_column(tmp_path):
    """Test validation with missing column."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestResult(TypedDict):
                number: int
                extra: str
            
            QUERY = """SELECT number FROM system.numbers LIMIT 1"""
        ''').strip()
    )

    is_valid, errors = validate_file(
        test_file, "clickhouse://admin:admin@localhost:8123"
    )
    assert not is_valid
    assert any(
        "Generated result expects column not in query result" in err for err in errors
    )
    assert any("extra" in err for err in errors)


def test_validate_file_extra_column(tmp_path):
    """Test validation with extra column in current schema."""
    test_file = tmp_path / "test.py"
    # Query returns both number and computed result, but TypedDict only has number
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestResult(TypedDict):
                number: int
            
            QUERY = """SELECT number, number * 2 AS doubled FROM system.numbers LIMIT 1"""
        ''').strip()
    )

    is_valid, errors = validate_file(
        test_file, "clickhouse://admin:admin@localhost:8123"
    )
    assert not is_valid
    assert any(
        "Query result has column not in generated result" in err for err in errors
    )
    assert any("doubled" in err for err in errors)


def test_validate_file_connection_error(tmp_path):
    """Test validation with connection error."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestResult(TypedDict):
                id: int
            
            QUERY = """SELECT 1 AS id"""
        ''').strip()
    )

    is_valid, errors = validate_file(test_file, "clickhouse://badhost:9999")
    assert not is_valid
    assert any("Failed to get schema from ClickHouse" in err for err in errors)


def test_extract_expected_parameters(tmp_path):
    """Test extracting parameters from Params class."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestParams:
                def __init__(self, user_id: int, name: str, age: int | None):
                    self.user_id = user_id
                    self.name = name
                    self.age = age
            
            class TestResult(TypedDict):
                id: int
            
            QUERY = """SELECT id FROM test WHERE id = {user_id:Int32}"""
        ''').strip()
    )

    params = extract_expected_parameters(test_file)
    assert params == {
        "user_id": "int",
        "name": "str",
        "age": "int | None",
    }


def test_extract_expected_parameters_no_params(tmp_path):
    """Test extracting parameters when no Params class exists."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestResult(TypedDict):
                id: int
            
            QUERY = """SELECT id FROM test"""
        ''').strip()
    )

    params = extract_expected_parameters(test_file)
    assert params == {}


def test_validate_file_parameter_mismatch_missing(tmp_path):
    """Test validation with missing parameter in generated code."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestParams:
                def __init__(self, user_id: int):
                    self.user_id = user_id
            
            class TestResult(TypedDict):
                number: int
            
            QUERY = """
            SELECT number 
            FROM system.numbers 
            WHERE number = {user_id:Int32} 
            AND number > {min_value:Int32}
            LIMIT 1
            """
        ''').strip()
    )

    is_valid, errors = validate_file(
        test_file, "clickhouse://admin:admin@localhost:8123"
    )
    assert not is_valid
    assert any(
        "Query parameter missing from generated parameters" in err for err in errors
    )
    assert any("min_value" in err for err in errors)


def test_validate_file_parameter_mismatch_extra(tmp_path):
    """Test validation with extra parameter in generated code."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestParams:
                def __init__(self, user_id: int, extra_param: str):
                    self.user_id = user_id
                    self.extra_param = extra_param
            
            class TestResult(TypedDict):
                number: int
            
            QUERY = """
            SELECT number 
            FROM system.numbers 
            WHERE number = {user_id:Int32}
            LIMIT 1
            """
        ''').strip()
    )

    is_valid, errors = validate_file(
        test_file, "clickhouse://admin:admin@localhost:8123"
    )
    assert not is_valid
    assert any(
        "Generated parameters has parameter not in query" in err for err in errors
    )
    assert any("extra_param" in err for err in errors)


def test_validate_file_parameter_type_mismatch(tmp_path):
    """Test validation with parameter type mismatch."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestParams:
                def __init__(self, user_id: str):
                    self.user_id = user_id
            
            class TestResult(TypedDict):
                number: int
            
            QUERY = """
            SELECT number 
            FROM system.numbers 
            WHERE number = {user_id:Int32}
            LIMIT 1
            """
        ''').strip()
    )

    is_valid, errors = validate_file(
        test_file, "clickhouse://admin:admin@localhost:8123"
    )
    assert not is_valid
    assert any("Parameter type mismatch for 'user_id'" in err for err in errors)
    assert any(
        "query expects int" in err and "generated parameters has str" in err
        for err in errors
    )


def test_validate_file_with_valid_parameters(tmp_path):
    """Test validation with matching parameters and schema."""
    test_file = tmp_path / "test.py"
    test_file.write_text(
        dedent('''
            from typing import TypedDict
            
            class TestParams:
                def __init__(self, limit_val: int):
                    self.limit_val = limit_val
            
            class TestResult(TypedDict):
                number: int
            
            QUERY = """
            SELECT number 
            FROM system.numbers 
            WHERE number < {limit_val:Int32}
            LIMIT 1
            """
        ''').strip()
    )

    is_valid, errors = validate_file(
        test_file, "clickhouse://admin:admin@localhost:8123"
    )
    assert is_valid
    assert errors == []
