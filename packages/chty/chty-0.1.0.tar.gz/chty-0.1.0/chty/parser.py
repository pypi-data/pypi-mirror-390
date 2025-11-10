"""Parse SQL files and extract ClickHouse parameterized query parameters."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class QueryParameter:
    """Represents a parameter extracted from a ClickHouse query."""

    name: str
    clickhouse_type: str


def parse_sql_file(file_path: str | Path) -> tuple[str, list[QueryParameter]]:
    """
    Parse a SQL file and extract the query string and parameters.

    Args:
        file_path: Path to the SQL file

    Returns:
        Tuple of (query_string, list of QueryParameter objects)

    Example:
        >>> query, params = parse_sql_file("example.sql")
        >>> params[0].name
        'multiplier'
        >>> params[0].clickhouse_type
        'Int32'
    """
    file_path = Path(file_path)
    query = file_path.read_text()

    parameters = extract_parameters(query)

    return query, parameters


def extract_parameters(query: str) -> list[QueryParameter]:
    """
    Extract parameters from a ClickHouse parameterized query.

    Parameters follow the format: {param_name:ClickHouseType}

    Args:
        query: SQL query string with ClickHouse parameterized syntax

    Returns:
        List of QueryParameter objects

    Example:
        >>> params = extract_parameters("SELECT * WHERE id = {id:Int32}")
        >>> params[0].name
        'id'
    """
    pattern = r"\{(\w+):([^}]+)\}"
    matches = re.findall(pattern, query)

    parameters = []
    seen = set()

    for name, ch_type in matches:
        if name not in seen:
            parameters.append(QueryParameter(name=name, clickhouse_type=ch_type))
            seen.add(name)

    return parameters
