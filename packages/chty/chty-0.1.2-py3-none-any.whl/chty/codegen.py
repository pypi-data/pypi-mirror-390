"""Generate typed Python code from parsed SQL queries."""

from __future__ import annotations

from pathlib import Path

from chty import __version__
from chty.parser import QueryParameter
from chty.typemapper import clickhouse_to_python_type, get_required_imports


def _generate_imports(
    parameters: list[QueryParameter],
    result_schema: list[tuple[str, str]] | None,
) -> str:
    """Generate import statements based on what's needed, properly ordered."""
    python_types = [clickhouse_to_python_type(p.clickhouse_type) for p in parameters]

    all_types = python_types.copy()
    if result_schema:
        all_types.extend(
            [clickhouse_to_python_type(col_type) for _, col_type in result_schema]
        )

    # Standard library imports
    stdlib_imports = []
    stdlib_imports.extend(sorted(get_required_imports(all_types)))

    typing_imports = []
    if parameters:
        typing_imports.append("Any, Dict")
    if result_schema:
        typing_imports.append("TypedDict")

    if typing_imports:
        stdlib_imports.append(f"from typing import {', '.join(typing_imports)}")

    # Third-party imports
    third_party_imports = []
    if result_schema:
        third_party_imports.append(
            "from clickhouse_connect.driver.client import Client"
        )

    # Combine with blank line between groups if both exist
    all_imports = stdlib_imports
    if third_party_imports:
        if stdlib_imports:
            all_imports.append("")
        all_imports.extend(third_party_imports)

    return "\n".join(all_imports)


def _generate_params_class(
    parameters: list[QueryParameter],
    class_name: str,
) -> str:
    """Generate the parameters class."""
    python_types = [clickhouse_to_python_type(p.clickhouse_type) for p in parameters]
    param_strs = [
        f"{p.name}: {py_type}" for p, py_type in zip(parameters, python_types)
    ]

    params = ",\n        ".join(["self", "*"] + param_strs)
    init_signature = f"def __init__(\n        {params},\n    ):"

    super_args = ",\n            ".join([f"{p.name}={p.name}" for p in parameters])
    super_call = f"super().__init__(\n            {super_args},\n        )"

    return f"""class {class_name}Params(Dict[str, Any]):
    {init_signature}
        {super_call}"""


def _generate_result_class(
    result_schema: list[tuple[str, str]],
    class_name: str,
) -> str:
    """Generate the result TypedDict class."""
    result_fields = "\n".join(
        f"    {col_name}: {clickhouse_to_python_type(col_type)}"
        for col_name, col_type in result_schema
    )
    return f"""class {class_name}Result(TypedDict):
{result_fields}"""


def _generate_query_class(
    result_schema: list[tuple[str, str]],
    class_name: str,
    has_parameters: bool,
) -> str:
    """Generate the query executor class."""
    field_items = [
        f'"{col}": "{clickhouse_to_python_type(col_type)}"'
        for col, col_type in result_schema
    ]
    fields = ",\n            ".join(field_items)
    expected_fields = f"self._expected_fields = {{\n            {fields},\n        }}"

    execute_sig = (
        f"parameters: {class_name}Params, **kwargs" if has_parameters else "**kwargs"
    )
    query_call_args = (
        "parameters=parameters, **kwargs" if has_parameters else "**kwargs"
    )

    return f"""class {class_name}Query:
    def __init__(self, client: Client, *, validate: bool = False):
        self.client = client
        self.query = QUERY
        self.validate = validate
        {expected_fields}

    def _validate_result(self, row: dict) -> None:
        if not self.validate:
            return
        missing = set(self._expected_fields.keys()) - set(row.keys())
        if missing:
            raise ValueError(f"Result missing expected fields: {{missing}}")
        extra = set(row.keys()) - set(self._expected_fields.keys())
        if extra:
            raise ValueError(f"Result has unexpected fields: {{extra}}")

    def execute(self, {execute_sig}) -> list[{class_name}Result]:
        result = self.client.query(self.query, {query_call_args})
        rows = [dict(zip(result.column_names, row)) for row in result.result_rows]
        if rows:
            self._validate_result(rows[0])
        return rows  # type: ignore[return-value]

    def execute_df(self, {execute_sig}) -> list[{class_name}Result]:
        df = self.client.query_df(self.query, {query_call_args})
        rows = df.to_dict("records")
        if rows:
            self._validate_result(rows[0])
        return rows  # type: ignore[return-value]"""


def generate_python_code(
    query: str,
    parameters: list[QueryParameter],
    class_name: str,
    result_schema: list[tuple[str, str]] | None = None,
) -> str:
    """
    Generate Python code with dict subclass for query parameters and TypedDict for results.

    Args:
        query: The SQL query string
        parameters: List of QueryParameter objects
        class_name: Name for the generated parameter class
        result_schema: Optional list of (column_name, clickhouse_type) tuples for result types

    Returns:
        Generated Python code as a string
    """
    parts = [
        f"# Auto-generated by chty v{__version__}",
        _generate_imports(parameters, result_schema),
    ]

    if parameters:
        parts.append(_generate_params_class(parameters, class_name))

    if result_schema:
        parts.append(_generate_result_class(result_schema, class_name))

    parts.append(f'QUERY = """{query.rstrip()}"""')

    if result_schema:
        parts.append(_generate_query_class(result_schema, class_name, bool(parameters)))

    return "\n\n\n".join(parts) + "\n"


def generate_file(
    sql_file: Path,
    output_dir: Path,
    query: str,
    parameters: list[QueryParameter],
    result_schema: list[tuple[str, str]] | None = None,
) -> Path:
    """
    Generate a Python file from a SQL file.

    Args:
        sql_file: Path to the source SQL file
        output_dir: Directory to write the generated Python file
        query: The SQL query string
        parameters: List of QueryParameter objects
        result_schema: Optional list of (column_name, clickhouse_type) tuples for result types

    Returns:
        Path to the generated Python file
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    class_name = sql_file.stem.replace("-", "_").replace(" ", "_")
    class_name = "".join(word.capitalize() for word in class_name.split("_"))

    code = generate_python_code(query, parameters, class_name, result_schema)

    output_file = output_dir / f"{sql_file.stem}.py"
    output_file.write_text(code)

    return output_file
