"""Validate generated code against live ClickHouse schema."""

from __future__ import annotations

import ast
import re
from pathlib import Path

from chty.parser import extract_parameters
from chty.schema import get_result_schema
from chty.typemapper import clickhouse_to_python_type


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


def extract_query_from_file(py_file: Path) -> str:
    """Extract the QUERY constant from a generated Python file."""
    content = py_file.read_text()
    match = re.search(r'QUERY = """(.+?)"""', content, re.DOTALL)
    if not match:
        raise ValidationError(f"Could not find QUERY in {py_file}")
    return match.group(1)


def extract_expected_schema(py_file: Path) -> dict[str, str]:
    """
    Extract the expected schema from a generated Python file.

    Returns a dict of {column_name: python_type}.
    """
    content = py_file.read_text()

    # Parse the Python file as AST
    tree = ast.parse(content)

    # Find the TypedDict class (ends with "Result")
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if it's a TypedDict result class
            if node.name.endswith("Result"):
                schema = {}
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(
                        item.target, ast.Name
                    ):
                        col_name = item.target.id
                        # Get the annotation as a string
                        py_type = ast.unparse(item.annotation)
                        schema[col_name] = py_type
                return schema

    # If no Result TypedDict found, file might not have result types
    return {}


def extract_expected_parameters(py_file: Path) -> dict[str, str]:
    """
    Extract the expected parameters from a generated Python file.

    Returns a dict of {param_name: python_type}.
    """
    content = py_file.read_text()

    # Parse the Python file as AST
    tree = ast.parse(content)

    # Find the Params class (ends with "Params")
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.endswith("Params"):
            # Find the __init__ method
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    params = {}
                    # Skip self and iterate through other arguments
                    for arg in item.args.args[1:]:  # Skip 'self'
                        if arg.annotation:
                            param_name = arg.arg
                            param_type = ast.unparse(arg.annotation)
                            params[param_name] = param_type
                    # Also check keyword-only arguments (after *)
                    for arg in item.args.kwonlyargs:
                        if arg.annotation:
                            param_name = arg.arg
                            param_type = ast.unparse(arg.annotation)
                            params[param_name] = param_type
                    return params

    # If no Params class found, file might not have parameters
    return {}


def _validate_parameters(
    query: str,
    expected_params: dict[str, str],
) -> list[str]:
    """Validate that query parameters match generated parameters."""
    errors = []

    query_params = extract_parameters(query)
    query_param_names = {p.name for p in query_params}
    expected_param_names = set(expected_params.keys())

    missing_params = query_param_names - expected_param_names
    if missing_params:
        errors.append(
            f"Query parameter missing from generated parameters: {', '.join(sorted(missing_params))}"
        )

    extra_params = expected_param_names - query_param_names
    if extra_params:
        errors.append(
            f"Generated parameters has parameter not in query: {', '.join(sorted(extra_params))}"
        )

    for param in query_params:
        if param.name in expected_params:
            expected_type = expected_params[param.name]
            actual_type = clickhouse_to_python_type(param.clickhouse_type)
            if expected_type != actual_type:
                errors.append(
                    f"Parameter type mismatch for '{param.name}': "
                    f"query expects {actual_type}, "
                    f"generated parameters has {expected_type}"
                )

    return errors


def _validate_result_schema(
    expected_schema: dict[str, str],
    actual_schema: dict[str, str],
) -> list[str]:
    """Validate that result schema matches between generated code and ClickHouse."""
    errors = []

    generated_cols = set(expected_schema.keys())
    actual_cols = set(actual_schema.keys())

    missing = generated_cols - actual_cols
    if missing:
        errors.append(
            f"Generated result expects column not in query result: {', '.join(sorted(missing))}"
        )

    extra = actual_cols - generated_cols
    if extra:
        errors.append(
            f"Query result has column not in generated result: {', '.join(sorted(extra))}"
        )

    for col in generated_cols & actual_cols:
        generated_type = expected_schema[col]
        actual_type = actual_schema[col]
        if generated_type != actual_type:
            errors.append(
                f"Result type mismatch for '{col}': "
                f"query returns {actual_type}, "
                f"generated result expects {generated_type}"
            )

    return errors


def validate_file(py_file: Path, db_url: str) -> tuple[bool, list[str]]:
    """
    Validate a generated Python file against live ClickHouse schema.

    Checks both parameters and result schema.

    Returns:
        (is_valid, list_of_errors)
    """
    try:
        query = extract_query_from_file(py_file)
        expected_params = extract_expected_parameters(py_file)
        expected_schema = extract_expected_schema(py_file)
    except Exception as e:
        return False, [f"Validation error: {e}"]

    errors = []
    errors.extend(_validate_parameters(query, expected_params))

    if not expected_schema:
        errors.append(
            f"No result schema found in {py_file}. "
            "File was likely generated without --db-url."
        )
        return False, errors

    try:
        current_schema = get_result_schema(query, db_url)
    except Exception as e:
        return False, errors + [f"Failed to get schema from ClickHouse: {e}"]

    actual_result_dict = {
        col: clickhouse_to_python_type(ch_type) for col, ch_type in current_schema
    }

    errors.extend(_validate_result_schema(expected_schema, actual_result_dict))

    return len(errors) == 0, errors
