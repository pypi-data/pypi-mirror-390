"""Map ClickHouse types to Python types."""

import re


def clickhouse_to_python_type(clickhouse_type: str) -> str:
    """
    Map a ClickHouse type to its Python type representation.

    Args:
        clickhouse_type: ClickHouse type string (e.g., 'Int32', 'String', 'Array(Int32)')

    Returns:
        Python type as a string for code generation

    Example:
        >>> clickhouse_to_python_type('Int32')
        'int'
        >>> clickhouse_to_python_type('String')
        'str'
        >>> clickhouse_to_python_type('Array(Int32)')
        'list[int]'
    """
    clickhouse_type = clickhouse_type.strip()

    if match := re.match(r"Nullable\((.+)\)", clickhouse_type):
        inner_type = clickhouse_to_python_type(match.group(1))
        return f"{inner_type} | None"

    if match := re.match(r"Array\((.+)\)", clickhouse_type):
        inner_type = clickhouse_to_python_type(match.group(1))
        return f"list[{inner_type}]"

    if match := re.match(r"Map\((.+),\s*(.+)\)", clickhouse_type):
        key_type = clickhouse_to_python_type(match.group(1))
        value_type = clickhouse_to_python_type(match.group(2))
        return f"dict[{key_type}, {value_type}]"

    if match := re.match(r"Tuple\((.+)\)", clickhouse_type):
        inner_types = match.group(1).split(",")
        python_types = [clickhouse_to_python_type(t.strip()) for t in inner_types]
        return f"tuple[{', '.join(python_types)}]"

    if clickhouse_type.startswith("Nested"):
        return "list[dict]"

    type_map = {
        # Integer types
        "Int8": "int",
        "Int16": "int",
        "Int32": "int",
        "Int64": "int",
        "Int128": "int",
        "Int256": "int",
        "UInt8": "int",
        "UInt16": "int",
        "UInt32": "int",
        "UInt64": "int",
        "UInt128": "int",
        "UInt256": "int",
        # Float types
        "Float32": "float",
        "Float64": "float",
        # String types
        "String": "str",
        "FixedString": "str",
        # Enum types
        "Enum8": "str",
        "Enum16": "str",
        "Enum": "str",
        # Boolean
        "Bool": "bool",
        # Date/Time types (check DateTime before Date to avoid prefix match)
        "DateTime64": "datetime",
        "DateTime": "datetime",
        "Date32": "date",
        "Date": "date",
        "Time64": "timedelta",
        "Time": "timedelta",
        # IP Address types
        "IPv4": "str",
        "IPv6": "str",
        # UUID
        "UUID": "str",
        # Decimal (represented as float for simplicity)
        "Decimal256": "float",
        "Decimal128": "float",
        "Decimal64": "float",
        "Decimal32": "float",
        "Decimal": "float",
        # JSON/Object types
        "JSON": "dict",
        "Object": "dict",
        # Dynamic types
        "Variant": "Any",
        "Dynamic": "Any",
    }

    for ch_prefix, py_type in type_map.items():
        if clickhouse_type.startswith(ch_prefix):
            return py_type

    return "Any"


def get_required_imports(python_types: list[str]) -> set[str]:
    """
    Determine which imports are needed based on the Python types used.

    Args:
        python_types: List of Python type strings

    Returns:
        Set of import statements needed

    Example:
        >>> get_required_imports(['int', 'date', 'datetime'])
        {'from datetime import date, datetime'}
    """
    imports = set()

    all_types = " ".join(python_types)

    datetime_imports = []
    if re.search(r"\bdatetime\b", all_types):
        datetime_imports.append("datetime")
    if re.search(r"\bdate\b", all_types):
        datetime_imports.append("date")
    if re.search(r"\btimedelta\b", all_types):
        datetime_imports.append("timedelta")

    if datetime_imports:
        imports.add(f"from datetime import {', '.join(sorted(datetime_imports))}")

    if "Any" in all_types:
        imports.add("from typing import Any")

    return imports
