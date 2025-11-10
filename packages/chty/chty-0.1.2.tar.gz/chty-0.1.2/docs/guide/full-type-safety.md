# Full Type Safety

This guide covers the recommended workflow for achieving end-to-end type safety with `chty`.

## Overview

Full type safety means having type information for **both** query inputs (parameters) and outputs (results). This requires connecting to ClickHouse at codegen time using the `--db-url` flag.

## How It Works

```mermaid
graph TD
    A[SQL File with Parameters] --> B[chty generate --db-url]
    B --> C[Connect to ClickHouse]
    C --> D[DESCRIBE TABLE query]
    D --> E[Extract Result Schema]
    E --> F[Generate Python Code]
    F --> G[Parameter + Result Types]
```

`chty` uses ClickHouse's `DESCRIBE TABLE (query)` feature to introspect the result schema **without executing the query**. This means:

- ✅ Safe for production databases
- ✅ Works with any SELECT query
- ✅ No data is actually queried
- ✅ Fast - just schema inspection

## Generation

### Command

```bash
chty generate queries/*.sql \
  --output generated/ \
  --db-url clickhouse://user:pass@host:port
```

### Process

1. **Parse SQL** - Extract parameters from `{param:Type}` syntax
2. **Replace Parameters** - Substitute with type-appropriate default values
3. **Describe Query** - Send `DESCRIBE TABLE (modified_query)` to ClickHouse
4. **Map Types** - Convert ClickHouse types to Python types
5. **Generate Code** - Create Python classes with full type annotations

## Generated Code

### Parameter Class

Type-safe input with constructor validation:

```python
class UsersParams(Dict[str, Any]):
    def __init__(self, *, min_age: int, pattern: str):
        super().__init__(min_age=min_age, pattern=pattern)
```

**Benefits:**
- Named parameters
- Type hints for IDE autocomplete
- Runtime type checking (constructor fails on wrong types)
- Compatible with clickhouse_connect (is a dict)

### Result TypedDict

Zero-overhead result typing:

```python
class UsersResult(TypedDict):
    user_id: int
    username: str
    email: str
    created_at: datetime
```

**Benefits:**
- IDE autocomplete for all fields
- Type checker validates field access
- Zero runtime overhead (just type hints)
- Dictionary interface (easy to work with)

### Query Wrapper

Type-safe execution methods:

```python
class UsersQuery:
    def __init__(self, client, *, validate: bool = False):
        self.client = client
        self.query = QUERY
        self.validate = validate

    def execute(
        self, 
        parameters: UsersParams, 
        **kwargs
    ) -> list[UsersResult]:
        result = self.client.query(
            self.query, 
            parameters=parameters, 
            **kwargs
        )
        rows = [dict(zip(result.column_names, row)) 
                for row in result.result_rows]
        if rows and self.validate:
            self._validate_result(rows[0])
        return rows  # type: ignore[return-value]

    def execute_df(
        self, 
        parameters: UsersParams, 
        **kwargs
    ) -> list[UsersResult]:
        df = self.client.query_df(
            self.query, 
            parameters=parameters, 
            **kwargs
        )
        rows = df.to_dict("records")
        if rows and self.validate:
            self._validate_result(rows[0])
        return rows  # type: ignore[return-value]
```

**Benefits:**
- Accepts typed parameters
- Returns typed results
- Forwards `**kwargs` to clickhouse_connect
- Optional runtime validation
- Clean, predictable API

## Usage

### Basic Pattern

```python
from generated.users import UsersParams, UsersQuery
import clickhouse_connect

# Setup
client = clickhouse_connect.get_client(host="localhost")

# Type-safe parameters
params = UsersParams(min_age=18, pattern="%john%")

# Type-safe query execution
query = UsersQuery(client)
results = query.execute(params)

# Type-safe result access
for user in results:
    print(user['username'])  # ✓ IDE autocompletes
    print(user['email'])     # ✓ Type checker validates
```

### With ClickHouse Options

Pass any `clickhouse_connect` options via `**kwargs`:

```python
results = query.execute(
    params,
    settings={
        'max_threads': 4,
        'max_execution_time': 30
    },
    query_formats={
        'datetime': 'string'
    }
)
```

### DataFrame Mode

Use `execute_df()` for DataFrame-based execution:

```python
results = query.execute_df(params, use_none=True)
```

Returns the same `list[UsersResult]` type.

## Type Safety Guarantees

### At Development Time

Type checkers (mypy, pyright) catch:

```python
# ❌ Wrong parameter type
params = UsersParams(min_age="not a number")

# ❌ Missing required parameter
params = UsersParams(min_age=18)

# ❌ Unknown parameter
params = UsersParams(min_age=18, pattern="%test%", wrong=123)

# ❌ Wrong result field
for user in results:
    print(user['usernam'])  # Typo!
```

### At Runtime

The generated code provides:

- **Parameter validation** - Constructor raises `TypeError` for wrong types
- **Result access** - Dictionary KeyError for wrong fields
- **Optional schema validation** - Enable with `validate=True`

## Best Practices

### 1. Always Use `--db-url` When Possible

Don't sacrifice result type safety unless you have no choice.

### 2. Use Development/Staging Database

Point `--db-url` at a dev or staging instance:

```bash
chty generate queries/*.sql \
  -o generated/ \
  --db-url clickhouse://dev-db:8123
```

### 3. Regenerate After Schema Changes

After altering tables or changing queries:

```bash
# Regenerate
chty generate queries/*.sql -o generated/ --db-url $DB_URL

# Validate (optional)
chty validate generated/*.py --db-url $DB_URL
```

### 4. Version Control Generated Code

Commit generated files to track changes:

```bash
git add generated/
git commit -m "Update generated types"
```

### 5. Add to CI/CD

Ensure generated code stays up to date:

```yaml
- name: Generate types
  run: chty generate queries/*.sql -o generated/ --db-url $DB_URL

- name: Validate types
  run: chty validate generated/*.py --db-url $DB_URL
```

## Limitations

### Query Restrictions

The query must be valid SQL that ClickHouse can analyze:

- ✅ Standard SELECT queries
- ✅ JOINs, subqueries, CTEs
- ✅ Aggregations, window functions
- ❌ Queries referencing non-existent tables (unless using system tables)

### Type Mapping Edge Cases

Some complex ClickHouse types map to `Any`:

- `Nested` types
- Custom `Enum` definitions
- Some exotic types

See [Type Mapping Reference](../reference/type-mapping.md) for complete details.

## Next Steps

- [Runtime Validation](runtime-validation.md) - Add optional schema checks
- [Schema Validation](schema-validation.md) - Detect drift in CI/CD
- [Examples](../reference/examples.md) - See real-world patterns

