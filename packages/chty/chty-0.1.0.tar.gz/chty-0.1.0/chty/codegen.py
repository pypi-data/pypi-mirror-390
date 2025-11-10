"""Generate typed Python code from parsed SQL queries."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from chty.parser import QueryParameter
from chty.typemapper import clickhouse_to_python_type, get_required_imports


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
    python_types = [clickhouse_to_python_type(p.clickhouse_type) for p in parameters]

    imports = ["from typing import Any, Dict"]
    if result_schema:
        imports.append("from typing import TypedDict")
    
    all_types = python_types.copy()
    if result_schema:
        all_types.extend([clickhouse_to_python_type(col_type) for _, col_type in result_schema])
    
    imports.extend(sorted(get_required_imports(all_types)))

    parts = ["\n".join(imports)]

    if parameters:
        init_params = ", ".join(
            f"{p.name}: {py_type}" for p, py_type in zip(parameters, python_types)
        )
        super_args = ", ".join(f"{p.name}={p.name}" for p in parameters)
        
        params_class = f'''
class {class_name}Params(Dict[str, Any]):
    def __init__(self, *, {init_params}):
        super().__init__({super_args})
'''
        parts.append(params_class.strip())

    if result_schema:
        result_fields = "\n".join(
            f"    {col_name}: {clickhouse_to_python_type(col_type)}"
            for col_name, col_type in result_schema
        )
        result_class = f'''
class {class_name}Result(TypedDict):
{result_fields}
'''
        parts.append(result_class.strip())

    parts.append(f'QUERY = """{query.rstrip()}"""')

    if result_schema:
        expected_fields_items = ', '.join(
            f'"{col}": "{clickhouse_to_python_type(col_type)}"' 
            for col, col_type in result_schema
        )
        
        query_class = f'''
class {class_name}Query:
    def __init__(self, client, *, validate: bool = False):
        self.client = client
        self.query = QUERY
        self.validate = validate
        self._expected_fields = {{{expected_fields_items}}}

    def _validate_result(self, row: dict) -> None:
        if not self.validate:
            return
        missing = set(self._expected_fields.keys()) - set(row.keys())
        if missing:
            raise ValueError(f"Result missing expected fields: {{missing}}")
        extra = set(row.keys()) - set(self._expected_fields.keys())
        if extra:
            raise ValueError(f"Result has unexpected fields: {{extra}}")

    def execute(self, parameters: {class_name}Params, **kwargs) -> list[{class_name}Result]:
        result = self.client.query(self.query, parameters=parameters, **kwargs)
        rows = [dict(zip(result.column_names, row)) for row in result.result_rows]
        if rows:
            self._validate_result(rows[0])
        return rows  # type: ignore[return-value]

    def execute_df(self, parameters: {class_name}Params, **kwargs) -> list[{class_name}Result]:
        df = self.client.query_df(self.query, parameters=parameters, **kwargs)
        rows = df.to_dict("records")
        if rows:
            self._validate_result(rows[0])
        return rows  # type: ignore[return-value]
'''
        parts.append(query_class.strip())

    return "\n\n".join(parts) + "\n"


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
