# Result Type Generation for chty

**Status: ✅ IMPLEMENTED**

## Problem

Currently, chty only generates typed **parameters** for queries. The result sets from `query_df()` are untyped DataFrames or dicts. We want to also generate typed result classes so users get type safety for both inputs and outputs.

## Requirements

1. **Must not execute heavy queries** - can't run `SELECT * FROM billion_row_table` at codegen time
2. **Must handle computed columns** - `SELECT number * 2 AS doubled` should infer type correctly
3. **Must work with parameterized queries** - handle `{param:Type}` syntax
4. **Should be optional** - not everyone has DB access at codegen time

## Approaches Tested

### Approach 1: `DESCRIBE TABLE (query)` ✅ RECOMMENDED

**Syntax:**

```sql
DESCRIBE TABLE (SELECT number * 2 AS doubled FROM system.numbers)
```

**Output:**

```
('doubled', 'UInt64', '', '', '', '', '')
```

**Pros:**

- ✅ Purpose-built for schema introspection - this is what it's designed for
- ✅ Guaranteed not to execute the query - pure analysis
- ✅ Returns clean structured data: `(column_name, type_string, ...)`
- ✅ Handles all ClickHouse expressions correctly (CTEs, subqueries, functions)
- ✅ Works with complex queries safely

**Cons:**

- Requires DB connection at codegen time (but that's the feature requirement)
- Need to replace `{param:Type}` with dummy values for schema detection

**Handling Parameters:**
Replace parameterized syntax with `NULL` or type-appropriate defaults:

```python
# Before: SELECT * WHERE id = {user_id:Int32}
# After:  SELECT * WHERE id = NULL
```

ClickHouse can still infer result schema even with NULL parameters.

---

### Approach 2: `LIMIT 0`

**Syntax:**

```sql
SELECT number * 2 AS doubled FROM system.numbers LIMIT 0
```

**Output:**

```python
result.column_names = ('doubled',)
result.column_types = (<UInt64 object>,)
```

**Pros:**

- ✅ Simple - just append `LIMIT 0`
- ✅ Fast - returns immediately with 0 rows
- ✅ Works with clickhouse_connect API directly

**Cons:**

- ⚠️ **May still execute CTEs and subqueries** depending on optimizer
- ⚠️ Not the intended use case - it's a hack
- ⚠️ Could have side effects (functions with side effects might still run)
- Returns type objects instead of strings (minor)

---

### Approach 3: Static SQL Parsing (sqlglot)

**Idea:** Parse SQL with sqlglot, extract column expressions, infer types statically.

**Pros:**

- No DB connection needed at codegen time

**Cons:**

- ❌ Cannot infer types for computed columns without full schema
- ❌ Would need to know table schemas somehow
- ❌ Complex expressions like `AVG(score)` are very hard to type
- ❌ Functions and type coercions are tricky
- Much more implementation work for worse results

---

## Recommendation: Use `DESCRIBE TABLE`

**Why:**

1. **Correctness** - It's the right tool for the job
2. **Safety** - Guaranteed not to execute expensive operations
3. **Completeness** - Handles all ClickHouse query features
4. **Simplicity** - Clean implementation

## Implementation Plan

### 1. Add CLI Flag

```bash
# Without DB - just params (current behavior)
chty generate queries/*.sql -o generated/

# With DB - params + result types (new feature)
chty generate queries/*.sql -o generated/ --db-url clickhouse://admin:admin@localhost:8123
```

### 2. Core Function

```python
def get_result_schema(
    query: str,
    db_url: str
) -> List[Tuple[str, str]]:
    """
    Get result schema from ClickHouse without executing the query.

    Args:
        query: SQL query with {param:Type} syntax
        db_url: ClickHouse connection URL

    Returns:
        List of (column_name, clickhouse_type) tuples
    """
    import re
    from urllib.parse import urlparse

    # Parse connection URL
    parsed = urlparse(db_url)
    client = clickhouse_connect.get_client(
        host=parsed.hostname,
        port=parsed.port or 8123,
        username=parsed.username,
        password=parsed.password,
    )

    # Replace parameters with NULL for schema detection
    # ClickHouse can still infer schema with NULL values
    safe_query = re.sub(r'\{(\w+):([^}]+)\}', 'NULL', query)

    # Get schema without executing
    result = client.query(f"DESCRIBE TABLE ({safe_query})")

    # Extract column names and types
    # result_rows = [('column_name', 'Type', '', '', '', '', ''), ...]
    return [(row[0], row[1]) for row in result.result_rows]
```

### 3. Type Constructs for Parameters vs Results

**Design Decision:**

- **Parameters**: `Dict[str, Any]` subclass (nice construction API)
- **Results**: `TypedDict` (zero runtime overhead)

**Rationale:**

Parameters are **constructed by user code once** per query:

- Small dict overhead is negligible
- Better DX: `SimpleParams(multiplier=3, limit=5)` vs `{"multiplier": 3, "limit": 5}`
- Runtime validation: catches typos in parameter names immediately
- No casting needed: IS a `Dict[str, Any]` so clickhouse_connect accepts it directly

Results are **constructed by ClickHouse many times** (one per row):

- Zero overhead: TypedDict is just a type annotation at runtime
- ClickHouse already returns dicts, no conversion needed
- Type safety: static checker validates field access
- Performance: no object construction or validation overhead

### 4. Generated Code

**Without `--db-url` (current):**

```python
from typing import Any, Dict

class SimpleParams(Dict[str, Any]):
    """Type-safe parameters for the query."""

    def __init__(self, *, multiplier: int, limit: int):
        super().__init__(multiplier=multiplier, limit=limit)

QUERY = "SELECT number * {multiplier:Int32} AS result ..."
```

**With `--db-url` (new):**

```python
from typing import Any, Dict, TypedDict

class SimpleParams(Dict[str, Any]):
    """Type-safe parameters for the query."""

    def __init__(self, *, multiplier: int, limit: int):
        super().__init__(multiplier=multiplier, limit=limit)

class SimpleResult(TypedDict):
    """Type-safe result row from the query."""
    number: int
    result: int

QUERY = "SELECT number * {multiplier:Int32} AS result ..."
```

### 5. Usage Example

```python
from generated.simple import SimpleParams, SimpleResult, QUERY
import clickhouse_connect

params = SimpleParams(multiplier=3, limit=5)
client = clickhouse_connect.get_client(host="localhost")

# Query returns DataFrame but we know the schema
result_df = client.query_df(QUERY, parameters=params)

# Convert to typed dicts
results: list[SimpleResult] = result_df.to_dict('records')

# Now we have full type safety!
for row in results:
    print(row["number"])   # Type checker knows this exists
    print(row["result"])   # Type checker knows this exists
    # print(row["typo"])   # Type checker catches this error!
```

## Edge Cases to Handle

1. **Parameters with NULL replacement** - test that schema detection works
2. **Complex expressions** - `CAST`, `CASE`, etc. should work fine with DESCRIBE
3. **CTEs** - DESCRIBE handles these correctly
4. **Subqueries** - DESCRIBE analyzes without executing
5. **Connection errors** - graceful fallback or clear error message

## Testing Strategy

```python
# test_result_schema.py
def test_describe_simple_query():
    schema = get_result_schema("SELECT 1 AS num", db_url)
    assert schema == [("num", "UInt8")]

def test_describe_computed_columns():
    schema = get_result_schema(
        "SELECT number * 2 AS doubled FROM system.numbers",
        db_url
    )
    assert schema == [("doubled", "UInt64")]

def test_describe_with_parameters():
    schema = get_result_schema(
        "SELECT number * {mult:Int32} AS result FROM system.numbers",
        db_url
    )
    assert schema == [("result", "UInt64")]  # Still infers correctly
```

## Migration Path

1. Implement `--db-url` flag as optional
2. Add `get_result_schema()` function
3. Update codegen to optionally generate result TypedDict
4. Add tests with real ClickHouse
5. Update docs with examples
6. Consider caching schemas to avoid repeated DB calls

## Summary

**Use `DESCRIBE TABLE (query)` approach** - it's safe, correct, and handles all cases properly. Make it an optional feature via `--db-url` flag so users without DB access can still use parameter generation.
