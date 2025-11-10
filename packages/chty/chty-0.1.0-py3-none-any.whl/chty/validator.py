"""Validate generated code against live ClickHouse schema."""

from __future__ import annotations

import ast
import re
from pathlib import Path

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


def validate_file(py_file: Path, db_url: str) -> tuple[bool, list[str]]:
    """
    Validate a generated Python file against live ClickHouse schema.

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    try:
        # Extract query and expected schema
        query = extract_query_from_file(py_file)
        expected_schema = extract_expected_schema(py_file)

        # If no expected schema, the file was generated without --db-url
        if not expected_schema:
            errors.append(
                f"No result schema found in {py_file}. "
                "File was likely generated without --db-url."
            )
            return False, errors

        # Get current schema from ClickHouse
        try:
            current_schema = get_result_schema(query, db_url)
        except Exception as e:
            errors.append(f"Failed to get schema from ClickHouse: {e}")
            return False, errors

        # Convert current schema to dict of {column_name: python_type}
        current_schema_dict = {
            col: clickhouse_to_python_type(ch_type) for col, ch_type in current_schema
        }

        # Compare schemas
        expected_cols = set(expected_schema.keys())
        current_cols = set(current_schema_dict.keys())

        # Check for missing columns
        missing = expected_cols - current_cols
        if missing:
            errors.append(f"Missing columns in current schema: {', '.join(missing)}")

        # Check for extra columns
        extra = current_cols - expected_cols
        if extra:
            errors.append(f"Extra columns in current schema: {', '.join(extra)}")

        # Check for type mismatches
        for col in expected_cols & current_cols:
            expected_type = expected_schema[col]
            current_type = current_schema_dict[col]
            if expected_type != current_type:
                errors.append(
                    f"Type mismatch for column '{col}': "
                    f"expected {expected_type}, got {current_type}"
                )

        return len(errors) == 0, errors

    except Exception as e:
        errors.append(f"Validation error: {e}")
        return False, errors
