# Runtime Validation

Add optional schema validation at query execution time.

## Overview

By default, result types are only checked statically (at development time). You can optionally enable runtime validation to catch schema mismatches:

```python
query = UsersQuery(client, validate=True)
results = query.execute(params)  # Validates schema!
```

## How It Works

When `validate=True`, the query wrapper:

1. Executes the query normally
2. Validates the **first row** against expected schema
3. Checks for missing or unexpected fields
4. Raises `ValueError` if mismatch detected

## Usage

```python
from generated.users import UsersParams, UsersQuery
import clickhouse_connect

client = clickhouse_connect.get_client(host="localhost")

# Enable validation
query = UsersQuery(client, validate=True)
params = UsersParams(min_age=18, pattern="%john%")

# This will validate the result schema
results = query.execute(params)
```

## What It Validates

### Missing Fields

```python
# Expected: user_id, username, email
# Actual: user_id, username (email missing)
ValueError: Result missing expected fields: {'email'}
```

### Extra Fields

```python
# Expected: user_id, username
# Actual: user_id, username, new_field
ValueError: Result has unexpected fields: {'new_field'}
```

### What It Doesn't Validate

- ❌ Field value types (Python doesn't enforce TypedDict)
- ❌ NULL values
- ❌ Data correctness

## Performance

Validation only checks the **first row**:

- ✅ O(1) cost regardless of result size
- ✅ Near-zero overhead
- ✅ Validates schema structure, not every value

```python
# Validates only first row!
results = query.execute(params)  # 1,000,000 rows
# Validation cost: ~same as 1 row
```

## When to Use

### ✅ Good Use Cases

- Development environments
- Test suites
- Catching schema changes early
- Debugging query issues

### ❌ When NOT to Use

- Production (adds overhead)
- Performance-critical paths
- When static type checking is enough

## Example

```python
import clickhouse_connect
from generated.users import UsersParams, UsersQuery

client = clickhouse_connect.get_client(host="localhost")

# Safe mode for development
if os.getenv("ENV") == "development":
    query = UsersQuery(client, validate=True)
else:
    query = UsersQuery(client)  # No validation in prod

params = UsersParams(min_age=18, pattern="%john%")
results = query.execute(params)
```

## Error Handling

```python
try:
    results = query.execute(params)
except ValueError as e:
    if "missing expected fields" in str(e):
        logger.error("Schema mismatch - regenerate types!")
    raise
```

## See Also

- [Schema Validation](schema-validation.md) - Validate at codegen/CI time
- [Error Handling](error-handling.md) - Handle validation failures

