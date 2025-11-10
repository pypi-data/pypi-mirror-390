# Quick Start

Get up and running with `chty` in 5 minutes!

## Step 1: Create a SQL File

Create a `.sql` file with ClickHouse parameterized queries:

```sql title="queries/users.sql"
SELECT user_id, username, email, created_at
FROM users
WHERE age >= {min_age:Int32}
  AND username LIKE {pattern:String}
ORDER BY created_at DESC
LIMIT {max_results:Int32}
```

!!! tip "ClickHouse Parameter Syntax"
    Use `{param_name:ClickHouseType}` syntax for parameters. `chty` will extract these and generate typed Python code.

## Step 2: Generate Type-Safe Code

Run `chty` to generate type-safe Python code:

```bash
chty generate queries/users.sql \
  --output generated/ \
  --db-url clickhouse://admin:admin@localhost:8123
```

This creates `generated/users.py` with:

- `UsersParams` - Type-safe parameter class
- `UsersResult` - TypedDict for result rows
- `UsersQuery` - Query wrapper with `execute()` and `execute_df()` methods

??? question "What if I don't have a ClickHouse server?"
    You can generate parameter types only (without `--db-url`):
    ```bash
    chty generate queries/users.sql --output generated/
    ```
    
    However, you'll miss out on result type safety. See [Parameter Types Only](../guide/parameter-types.md) for details.

## Step 3: Use the Generated Code

```python
from generated.users import UsersParams, UsersQuery
from datetime import datetime
import clickhouse_connect

# Create client
client = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="admin",
    password="admin"
)

# Create type-safe parameters and query
params = UsersParams(
    min_age=18,
    pattern="%john%",
    max_results=10
)
query = UsersQuery(client)

# Execute with full type safety
results = query.execute(params)

for user in results:
    # ✓ IDE autocompletes all fields
    # ✓ Type checker knows the types
    print(f"{user['username']}: {user['email']}")
```

## What You Get

### Type-Safe Parameters

```python
# ✅ Type checker catches these
params = UsersParams(
    min_age="not a number",  # ❌ Type error: expected int
    pattern="%john%",
    # ❌ Missing max_results
)

params = UsersParams(
    min_age=18,
    wrong_param=123  # ❌ Unknown parameter
)
```

### Type-Safe Results

```python
results = query.execute(params)

for user in results:
    # ✅ IDE knows these fields exist
    print(user['username'])
    print(user['email'])
    print(user['created_at'])
    
    # ❌ Type checker catches typos
    print(user['usernam'])  # Unknown field!
```

### Multiple Execution Methods

```python
# Standard query
results = query.execute(params)

# DataFrame-based (returns same TypedDict list)
results = query.execute_df(params)

# Pass clickhouse_connect options
results = query.execute(params, settings={'max_threads': 4})
```

## Next Steps

<div class="grid cards" markdown>

- :material-book-open-variant: **[Basic Usage](basic-usage.md)**

    Learn all the fundamental concepts

- :material-shield-check: **[Runtime Validation](../guide/runtime-validation.md)**

    Add optional schema validation

- :material-alert-decagram: **[Schema Validation](../guide/schema-validation.md)**

    Detect schema drift in CI/CD

- :material-code-braces: **[Examples](../reference/examples.md)**

    See more real-world examples

</div>

