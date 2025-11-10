# chty Usage Guide

## Quick Start

### 1. Install chty

```bash
# Run directly without installation (recommended)
uvx chty

# Or install globally
uv tool install chty

# Or use pip/pipx
pip install chty
```

### 2. Create a SQL file with ClickHouse parameterized queries

```sql
-- queries/my_query.sql
SELECT *
FROM users
WHERE age >= {min_age:Int32}
AND name LIKE {pattern:String}
```

### 3. Generate typed Python code

**Recommended:** Generate with full type safety (parameters + results)

```bash
chty generate queries/my_query.sql --output generated/ --db-url clickhouse://admin:admin@localhost:8123
```

This generates:

```python
# generated/my_query.py
from typing import Any, Dict
from typing import TypedDict


class MyQueryParams(Dict[str, Any]):
    """Type-safe parameters for the query."""

    def __init__(self, *, min_age: int, pattern: str):
        super().__init__(min_age=min_age, pattern=pattern)


class MyQueryResult(TypedDict):
    """Type-safe result row from the query."""
    id: int
    name: str
    age: int
    email: str


QUERY = """SELECT * FROM users WHERE age >= {min_age:Int32} AND name LIKE {pattern:String}"""


class MyQueryQuery:
    """Type-safe query executor for myquery.sql"""

    def __init__(self, client):
        self.client = client
        self.query = QUERY

    def execute(self, parameters: MyQueryParams, **kwargs) -> list[MyQueryResult]:
        """Execute query and return typed results."""
        result = self.client.query(self.query, parameters=parameters, **kwargs)
        return [
            dict(zip(result.column_names, row))
            for row in result.result_rows
        ]

    def execute_df(self, parameters: MyQueryParams, **kwargs) -> list[MyQueryResult]:
        """Execute query using DataFrame and return typed results."""
        df = self.client.query_df(self.query, parameters=parameters, **kwargs)
        return df.to_dict("records")
```

**Fallback:** If you don't have ClickHouse access at codegen time, generate parameters only:

```bash
chty generate queries/my_query.sql --output generated/
```

This generates only the `MyQueryParams` class and `QUERY` constant. You won't get result types or the query wrapper class.

### 4. Use the generated code

```python
from generated.my_query import MyQueryParams, MyQueryQuery
import clickhouse_connect

# Create client
client = clickhouse_connect.get_client(host="localhost")

# Create type-safe parameters and query wrapper
params = MyQueryParams(min_age=18, pattern="%john%")
query = MyQueryQuery(client)

# Execute with full type safety - IDE autocompletes all result fields!
results = query.execute(params)
for row in results:
    print(f"{row['name']} ({row['age']}) - {row['email']}")
    # ✓ Type checker knows: name, age, email, and their types

# Pass native clickhouse_connect options
results = query.execute(params, settings={'max_threads': 4})

# Or use DataFrame method
results = query.execute_df(params, use_none=True)
```

**Note:** If you only generated parameters (no `--db-url`), use the ClickHouse client directly:

```python
from generated.my_query import QUERY, MyQueryParams
import clickhouse_connect

client = clickhouse_connect.get_client(host="localhost")
params = MyQueryParams(min_age=18, pattern="%john%")
result = client.query_df(QUERY, parameters=params)  # No result type safety
```

## Type Safety Benefits

With chty, type checkers (mypy, pyright) will catch errors at development time:

```python
# Type error: wrong type
params = MyQueryParams(min_age="not a number", pattern="%john%")

# Type error: missing required parameter
params = MyQueryParams(min_age=18)

# Type error: unexpected keyword argument
params = MyQueryParams(minimum_age=18, pattern="%john%")
```

## Supported ClickHouse Types

| ClickHouse Type                  | Python Type     |
| -------------------------------- | --------------- |
| Int8, Int32, Int64, UInt32, etc. | `int`           |
| Float32, Float64                 | `float`         |
| String, FixedString              | `str`           |
| Bool                             | `bool`          |
| Date, Date32                     | `date`          |
| DateTime, DateTime64             | `datetime`      |
| Array(T)                         | `list[T]`       |
| Nullable(T)                      | `T \| None`     |
| Map(K, V)                        | `dict[K, V]`    |
| Tuple(T1, T2)                    | `tuple[T1, T2]` |

## Running Tests

```bash
uv run pytest tests/ -v
```

## Result Type Generation

Result type generation uses ClickHouse's `DESCRIBE TABLE (query)` to introspect the schema at codegen time without executing the query.

**Benefits:**

- ✅ Type-safe result access with full IDE autocomplete
- ✅ Multiple execution methods (`execute()` and `execute_df()`)
- ✅ Pass native clickhouse_connect options via `**kwargs`
- ✅ Transparent error handling - all exceptions propagate
- ✅ Zero runtime overhead (TypedDict is just a type annotation)

**How it works:**

1. Parameters like `{param:Type}` are replaced with type-appropriate default values
2. ClickHouse analyzes the query structure without executing it
3. Column names and types are extracted and mapped to Python types
4. A TypedDict and query wrapper class are generated

**Generated Methods:**

- `execute(params, **kwargs)` - Uses `client.query()`, returns typed list
- `execute_df(params, **kwargs)` - Uses `client.query_df()`, returns typed list

**Important:** The query must be valid SQL that ClickHouse can analyze. It doesn't need to reference existing tables if using intrinsic functions or system tables.

## Runtime Validation

By default, result types are only checked statically (at development time). You can optionally enable runtime validation:

```python
from generated.my_query import MyQueryParams, MyQueryQuery
import clickhouse_connect

# Create client
client = clickhouse_connect.get_client(host="localhost")

# Create params and query with validation enabled
params = MyQueryParams(min_age=18, pattern="%john%")
query = MyQueryQuery(client, validate=True)

# This will raise ValueError if the result schema doesn't match
results = query.execute(params)
```

**When to use validation:**

- ✅ During development to catch schema changes early
- ✅ In test environments
- ✅ When dealing with dynamic queries or views
- ❌ In production (adds overhead) - rely on static type checking instead

**What it validates:**

- Missing expected fields → `ValueError`
- Unexpected extra fields → `ValueError`

**What it doesn't validate:**

- Field value types (Python doesn't enforce TypedDict at runtime)
- NULL values in non-nullable fields

**Performance:**

- Only validates the **first row** to check schema structure
- Near-zero overhead even with large result sets
- O(1) validation cost regardless of result size

## Error Handling

The wrapper class is transparent - all errors propagate normally:

| Error Type                           | Caught at Development? | Throws at Runtime?  |
| ------------------------------------ | ---------------------- | ------------------- |
| Wrong param type                     | ✅ Type checker        | ✅ ClickHouse       |
| Missing param                        | ✅ Type checker        | ✅ Python TypeError |
| Connection/SQL errors                | ❌                     | ✅ ClickHouse       |
| Wrong result field                   | ✅ Type checker        | ✅ KeyError         |
| Schema mismatch (with validate=True) | ❌                     | ✅ ValueError       |

## Schema Validation

The `validate` command checks generated code against the current ClickHouse schema to detect drift:

```bash
chty validate generated/*.py --db-url clickhouse://admin:admin@localhost:8123
```

### What It Validates

- **Missing columns**: Expected columns that no longer exist in the query result
- **Extra columns**: New columns in the query result not in the generated code
- **Type mismatches**: Columns where the type has changed (e.g., `Int32` → `String`)

### Exit Codes

- `0`: All files are valid, no schema drift detected
- `1`: One or more files have schema mismatches

### Example Output

**Valid schema:**

```bash
$ chty validate generated/simple.py --db-url clickhouse://localhost:8123
Validating 1 file(s) against ClickHouse...

Checking generated/simple.py...
  ✓ Valid

✓ All 1 file(s) are valid!
```

**Schema drift detected:**

```bash
$ chty validate generated/simple.py --db-url clickhouse://localhost:8123
Validating 1 file(s) against ClickHouse...

Checking generated/simple.py...
  ✗ Validation failed:
    - Missing columns in current schema: old_column
    - Type mismatch for column 'count': expected str, got int

✗ 1 file(s) failed validation, 0 passed
```

### Use in CI/CD

Add to your CI pipeline to catch breaking schema changes:

```yaml
# .github/workflows/validate.yml
- name: Validate ClickHouse schemas
  run: |
    chty validate generated/*.py --db-url $CLICKHOUSE_URL
```

## Running Examples

```bash
# Generate with parameter types only
chty generate examples/queries/*.sql --output examples/generated/

# Generate with parameter AND result types (requires ClickHouse)
chty generate examples/queries/simple.sql --output examples/generated/ --db-url clickhouse://admin:admin@localhost:8123

# Validate generated code
chty validate examples/generated/simple.py --db-url clickhouse://admin:admin@localhost:8123

# Run demo (requires ClickHouse server on localhost)
cd /Users/treygilliland/code/chty && uv run python examples/demo.py
```
