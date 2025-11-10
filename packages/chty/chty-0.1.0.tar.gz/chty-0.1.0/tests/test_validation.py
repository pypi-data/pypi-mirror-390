"""Tests for runtime validation feature."""

from chty.codegen import generate_python_code
from chty.parser import QueryParameter


def test_validation_disabled_by_default():
    """Test that validation is disabled by default."""
    query = "SELECT id, name FROM users WHERE id = {user_id:Int32}"
    params = [QueryParameter("user_id", "Int32")]
    result_schema = [("id", "Int64"), ("name", "String")]

    code = generate_python_code(query, params, "TestQuery", result_schema)

    assert "def __init__(self, client, *, validate: bool = False):" in code
    assert "self.validate = validate" in code
    assert "_validate_result" in code


def test_validation_checks_expected_fields():
    """Test that expected fields are stored."""
    query = "SELECT num, text FROM test"
    params = []
    result_schema = [("num", "Int32"), ("text", "String")]

    code = generate_python_code(query, params, "TestQuery", result_schema)

    assert '"num": "int"' in code
    assert '"text": "str"' in code
    assert "self._expected_fields" in code


def test_validation_function_checks_missing_fields():
    """Test that validation checks for missing fields."""
    query = "SELECT id FROM test"
    params = []
    result_schema = [("id", "Int32")]

    code = generate_python_code(query, params, "TestQuery", result_schema)

    assert "missing = set(self._expected_fields.keys()) - set(row.keys())" in code
    assert 'raise ValueError(f"Result missing expected fields: {missing}")' in code


def test_validation_function_checks_extra_fields():
    """Test that validation checks for unexpected fields."""
    query = "SELECT id FROM test"
    params = []
    result_schema = [("id", "Int32")]

    code = generate_python_code(query, params, "TestQuery", result_schema)

    assert "extra = set(row.keys()) - set(self._expected_fields.keys())" in code
    assert 'raise ValueError(f"Result has unexpected fields: {extra}")' in code


def test_validation_integrated_in_execute():
    """Test that validation is called in execute methods."""
    query = "SELECT id FROM test"
    params = []
    result_schema = [("id", "Int32")]

    code = generate_python_code(query, params, "TestQuery", result_schema)

    # Check both execute methods call validation on first row only
    assert code.count("self._validate_result(rows[0])") == 2  # Once in execute, once in execute_df
    assert "if rows:" in code  # Validation only happens if there are rows


def test_validation_raises_documented():
    """Test that ValueError is raised in validation code."""
    query = "SELECT id FROM test"
    params = []
    result_schema = [("id", "Int32")]

    code = generate_python_code(query, params, "TestQuery", result_schema)

    # Check that ValueError is raised for validation errors
    assert "raise ValueError" in code
    assert "missing expected fields" in code
    assert "unexpected fields" in code

