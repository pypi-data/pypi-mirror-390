"""Tests for validator module."""

from pathlib import Path
from textwrap import dedent

import pytest

from chty.validator import extract_query_from_file, extract_expected_schema, validate_file, ValidationError


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
    
    is_valid, errors = validate_file(test_file, "clickhouse://admin:admin@localhost:8123")
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
    
    is_valid, errors = validate_file(test_file, "clickhouse://admin:admin@localhost:8123")
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
    
    is_valid, errors = validate_file(test_file, "clickhouse://admin:admin@localhost:8123")
    assert not is_valid
    assert any("Type mismatch" in err for err in errors)
    assert any("expected str, got int" in err for err in errors)


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
    
    is_valid, errors = validate_file(test_file, "clickhouse://admin:admin@localhost:8123")
    assert not is_valid
    assert any("Missing columns" in err for err in errors)
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
    
    is_valid, errors = validate_file(test_file, "clickhouse://admin:admin@localhost:8123")
    assert not is_valid
    assert any("Extra columns" in err for err in errors)
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

