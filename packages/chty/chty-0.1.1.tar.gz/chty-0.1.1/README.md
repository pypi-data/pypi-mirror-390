# chty

End-to-end type-safe ClickHouse query codegen from SQL files.

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://treygilliland.github.io/chty/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
# Run directly without installation
uvx chty

# Or install globally
uv tool install chty

# Or use pip/pipx
pip install chty
```

## Quick Start

Create a `.sql` file with ClickHouse parameterized queries:

```sql
-- queries/example.sql
SELECT number, number * {multiplier:Int32} AS result
FROM system.numbers
WHERE number < {limit:Int32}
```

Generate fully type-safe Python code:

```bash
chty generate queries/*.sql --output generated/ --db-url clickhouse://user:pass@host:port
```

Use the generated code with full type safety:

```python
from generated.example import ExampleParams, ExampleQuery
import clickhouse_connect

client = clickhouse_connect.get_client(host="localhost")
params = ExampleParams(multiplier=3, limit=5)
query = ExampleQuery(client)

# Execute with full IDE autocomplete on parameters and results
results = query.execute(params)
for row in results:
    print(f"Number: {row['number']}, Result: {row['result']}")
```

## Features

- ✅ **Type-safe parameters** - Catch parameter errors at development time
- ✅ **Type-safe results** - Full autocomplete for result fields (with `--db-url`)
- ✅ **Schema validation** - Detect schema drift with `chty validate`
- ✅ **Multiple execution methods** - `execute()` and `execute_df()` for DataFrames
- ✅ **Optional runtime validation** - Validate result schema at runtime
- ✅ **Zero runtime overhead** - TypedDict is just type annotations

## Why chty?

ClickHouse queries in Python lack type safety. `chty` connects your SQL queries directly to Python's type system:

**Without chty:**
- ❌ No autocomplete for query parameters or results
- ❌ Errors only caught at runtime
- ❌ No way to detect schema drift

**With chty:**
- ✅ Full type safety from SQL to Python
- ✅ IDE autocomplete everywhere
- ✅ Catch errors at development time
- ✅ Detect schema changes in CI/CD

## Documentation

Full documentation is available at [https://treygilliland.github.io/chty/](https://treygilliland.github.io/chty/)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.
