# Installation

## Requirements

- Python 3.10 or higher
- [A ClickHouse server](https://clickhouse.com/docs/en/install) (optional, for full type safety with `--db-url`)

## Install chty

=== "uvx (recommended)"
```bash # Run directly without installation
uvx chty --help

    # Use in your workflow
    uvx chty generate queries/*.sql -o generated/
    ```

=== "uv tool"
```bash # Install globally
uv tool install chty

    # Then use anywhere
    chty --help
    ```

=== "pip"
`bash
    pip install chty
    `

=== "pipx"
`bash
    pipx install chty
    `

=== "From source"
`bash
    git clone https://github.com/treygilliland/chty.git
    cd chty
    uv pip install -e ".[dev]"
    `

## Verify Installation

```bash
chty --help
```

You should see:

```
Usage: chty [OPTIONS] COMMAND [ARGS]...

Type-safe ClickHouse query parameter and result codegen

Commands:
  generate  Generate typed Python code from SQL files
  validate  Validate generated code against current ClickHouse schema
```

## Optional: ClickHouse Server

For full type safety (parameter + result types), you'll need access to a ClickHouse server at codegen time.

### Options

- **Local**: Install [ClickHouse locally](https://clickhouse.com/docs/en/install) or use [Docker](https://hub.docker.com/r/clickhouse/clickhouse-server)
- **Cloud**: Sign up for a free trial at [ClickHouse Cloud](https://clickhouse.cloud)

### Connection String Format

**Local ClickHouse:**

```
clickhouse://username:password@host:port
```

**ClickHouse Cloud:**

```
https://username:password@host:port
```

Examples:

```bash
# Local ClickHouse (default user, no password)
clickhouse://default:@localhost:8123

# Local ClickHouse with authentication
clickhouse://admin:password@localhost:8123

# ClickHouse Cloud
https://portal_read:password@abc123.us-east1.gcp.clickhouse.cloud:8443
```

## Next Steps

- [Quick Start](quick-start.md) - Get started in 5 minutes
- [Basic Usage](basic-usage.md) - Learn the fundamentals
