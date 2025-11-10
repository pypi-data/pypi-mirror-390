"""Schema introspection for ClickHouse queries."""

from __future__ import annotations

import re
from urllib.parse import urlparse

import clickhouse_connect


def _get_default_value_for_type(clickhouse_type: str) -> str:
    """Get a default value for a ClickHouse type for schema introspection."""
    clickhouse_type = clickhouse_type.strip()
    
    if clickhouse_type.startswith("Int") or clickhouse_type.startswith("UInt"):
        return "0"
    elif clickhouse_type.startswith("Float") or clickhouse_type.startswith("Decimal"):
        return "0.0"
    elif clickhouse_type.startswith("String") or clickhouse_type.startswith("FixedString"):
        return "''"
    elif clickhouse_type.startswith("Bool"):
        return "false"
    elif clickhouse_type.startswith("Date") or clickhouse_type.startswith("DateTime"):
        return "'1970-01-01'"
    elif clickhouse_type.startswith("UUID"):
        return "'00000000-0000-0000-0000-000000000000'"
    elif clickhouse_type.startswith("Array"):
        return "[]"
    elif clickhouse_type.startswith("Map"):
        return "map()"
    elif clickhouse_type.startswith("Nullable"):
        inner_match = re.match(r"Nullable\((.+)\)", clickhouse_type)
        if inner_match:
            inner_type = inner_match.group(1)
            return _get_default_value_for_type(inner_type)
        return "NULL"
    else:
        return "NULL"


def get_result_schema(query: str, db_url: str) -> list[tuple[str, str]]:
    """
    Get result schema from ClickHouse without executing the query.

    Args:
        query: SQL query with {param:Type} syntax
        db_url: ClickHouse connection URL (e.g., clickhouse://user:pass@host:port)

    Returns:
        List of (column_name, clickhouse_type) tuples

    Raises:
        ValueError: If db_url is invalid
        Exception: If connection or query fails
    """
    parsed = urlparse(db_url)

    if parsed.scheme not in ("clickhouse", "clickhouse+native"):
        raise ValueError(
            f"Invalid db_url scheme: {parsed.scheme}. "
            "Expected 'clickhouse://user:pass@host:port'"
        )

    client = clickhouse_connect.get_client(
        host=parsed.hostname or "localhost",
        port=parsed.port or 8123,
        username=parsed.username or "default",
        password=parsed.password or "",
    )

    def replace_param(match):
        param_name = match.group(1)
        param_type = match.group(2)
        default_val = _get_default_value_for_type(param_type)
        return default_val

    safe_query = re.sub(r"\{(\w+):([^}]+)\}", replace_param, query)

    result = client.query(f"DESCRIBE TABLE ({safe_query})")

    return [(row[0], row[1]) for row in result.result_rows]

