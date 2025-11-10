# chty

<p align="center">
  <strong>End-to-end type-safe ClickHouse query codegen from SQL files</strong>
</p>

<p align="center">
  <a href="https://github.com/treygilliland/chty"><img src="https://img.shields.io/badge/GitHub-Repository-blue?logo=github" alt="GitHub"></a>
  <a href="https://pypi.org/project/chty/"><img src="https://img.shields.io/pypi/v/chty" alt="PyPI"></a>
  <a href="https://github.com/treygilliland/chty/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"></a>
</p>

---

## What is chty?

**chty** (ClickHouse Type) is a code generation tool that brings **full type safety** to your ClickHouse queries in Python. Write your SQL in `.sql` files, and `chty` generates type-safe Python code with:

- ✅ **Type-safe parameters** - IDE autocomplete and type checking for query inputs
- ✅ **Type-safe results** - Full autocomplete for query result fields
- ✅ **Schema validation** - Detect schema drift in CI/CD pipelines
- ✅ **Zero runtime overhead** - Pure type annotations, no performance cost
- ✅ **Multiple execution methods** - Support for both query and DataFrame workflows

## The Problem

Without `chty`, ClickHouse queries in Python lack type safety:

```python
# ❌ No type safety
result = client.query(
    "SELECT name, age FROM users WHERE id = {id:Int32}",
    parameters={"id": "not_a_number"}  # Runtime error!
)

for row in result.result_rows:
    print(row[0], row[1])  # What fields? What types? 🤷
```

## The Solution

With `chty`, you get end-to-end type safety:

```python
# ✅ Full type safety
params = UserQueryParams(id=123)  # Type checked!
query = UserQuery(client)

results = query.execute(params)
for row in results:
    print(row['name'], row['age'])  # IDE knows these fields exist!
    # ✓ Autocomplete works
    # ✓ Type checker catches errors
```

## Quick Example

**1. Write your SQL:**

```sql
-- queries/users.sql
SELECT user_id, username, email
FROM users
WHERE age >= {min_age:Int32}
AND created_at >= {start_date:DateTime}
```

**2. Generate type-safe Python code:**

```bash
chty generate queries/*.sql -o generated/ --db-url clickhouse://localhost:8123
```

**3. Use it with full type safety:**

```python
from generated.users import UsersParams, UsersQuery
import clickhouse_connect

client = clickhouse_connect.get_client(host="localhost")
params = UsersParams(min_age=18, start_date=datetime(2020, 1, 1))
query = UsersQuery(client)

results = query.execute(params)
for user in results:
    print(f"{user['username']}: {user['email']}")
    # ✓ Full IDE autocomplete for all fields
```

## Key Features

### End-to-End Type Safety

Connect your SQL directly to Python's type system. Parameters AND results are fully typed.

### Schema Introspection

`chty` uses ClickHouse's `DESCRIBE TABLE` to introspect query schemas at codegen time—no heavy queries needed.

### Schema Drift Detection

Add `chty validate` to your CI pipeline to catch schema changes before they break production:

```bash
chty validate generated/*.py --db-url $CLICKHOUSE_URL
```

### Developer Experience

- **IDE Autocomplete**: Works everywhere—parameters, results, all fields
- **Type Checking**: mypy and pyright catch errors at development time
- **Clean Generated Code**: Human-readable, production-ready Python
- **Flexible**: Works with or without database access at codegen time

## Installation

=== "uvx (recommended)"
    ```bash
    # Run directly without installation
    uvx chty
    ```

=== "uv tool install"
    ```bash
    # Install globally
    uv tool install chty
    ```

=== "pip"
    ```bash
    pip install chty
    ```

=== "pipx"
    ```bash
    pipx install chty
    ```

## Next Steps

<div class="grid cards" markdown>

- :material-clock-fast: **[Quick Start](getting-started/quick-start.md)**

    Get up and running in 5 minutes

- :material-book-open-variant: **[User Guide](guide/full-type-safety.md)**

    Learn about all features in depth

- :material-code-braces: **[CLI Reference](reference/cli.md)**

    Complete command reference

- :material-github: **[Examples](reference/examples.md)**

    See real-world usage examples

</div>

## Why chty?

<div class="grid" markdown>

!!! success "With chty"
    - ✅ Full type safety from SQL to Python
    - ✅ IDE autocomplete for parameters AND results
    - ✅ Catch errors at development time
    - ✅ Detect schema changes in CI/CD
    - ✅ Zero runtime overhead

!!! failure "Without chty"
    - ❌ No autocomplete for query parameters
    - ❌ No autocomplete for result fields
    - ❌ Errors only caught at runtime
    - ❌ No way to detect schema drift
    - ❌ Manual type annotations

</div>

## Community

- **GitHub**: [treygilliland/chty](https://github.com/treygilliland/chty)
- **Issues**: [Report bugs or request features](https://github.com/treygilliland/chty/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/treygilliland/chty/discussions)

## License

MIT License - see [LICENSE](https://github.com/treygilliland/chty/blob/main/LICENSE) for details.

