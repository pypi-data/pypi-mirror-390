# Parameter Types Only

Generate parameter types without database access.

## When to Use

Use parameter-only mode when:

- ❌ No ClickHouse access at codegen time
- ❌ Working offline or in restricted environment
- ❌ Early development before database exists

!!! warning "Limited Type Safety"
    Without `--db-url`, you only get parameter type safety. Result types require database introspection.

## Usage

```bash
chty generate queries/*.sql --output generated/
```

## Generated Code

### Parameter Class Only

```python
class UsersParams(Dict[str, Any]):
    def __init__(self, *, min_age: int, pattern: str):
        super().__init__(min_age=min_age, pattern=pattern)

QUERY = """SELECT * FROM users WHERE age >= {min_age:Int32}..."""
```

**No TypedDict, no query wrapper.**

## Using Generated Code

You must use the clickhouse_connect client directly:

```python
from generated.users import QUERY, UsersParams
import clickhouse_connect

client = clickhouse_connect.get_client(host="localhost")
params = UsersParams(min_age=18, pattern="%john%")

# Use client directly - no result type safety
result = client.query(QUERY, parameters=params)
for row in result.result_rows:
    # No autocomplete for fields
    print(row[0], row[1])  # What are these? 🤷
```

## Limitations

- ❌ No result type safety
- ❌ No query wrapper class
- ❌ Cannot use `chty validate`
- ❌ No IDE autocomplete for results
- ❌ Manual index access to result rows

## Upgrading to Full Type Safety

When you get database access:

```bash
# Regenerate with full type safety
chty generate queries/*.sql -o generated/ --db-url clickhouse://localhost:8123
```

This adds:
- ✅ Result TypedDict
- ✅ Query wrapper class
- ✅ Schema validation support

## See Also

- [Full Type Safety](full-type-safety.md) - Recommended workflow
- [CLI Reference](../reference/cli.md) - Command options

