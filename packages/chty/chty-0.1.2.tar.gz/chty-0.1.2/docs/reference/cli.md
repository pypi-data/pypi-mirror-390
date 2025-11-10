# CLI Reference

Complete reference for all `chty` commands.

## Commands

### `chty generate`

Generate typed Python code from SQL files.

```bash
chty generate [OPTIONS] SQL_FILES...
```

#### Arguments

- `SQL_FILES...` - One or more SQL files to process (supports glob patterns)

#### Options

- `--output`, `-o` `PATH` - Output directory for generated Python files (default: `generated`)
- `--db-url` `TEXT` - ClickHouse connection URL for full type safety (recommended)

#### Examples

```bash
# Full type safety (recommended)
chty generate queries/*.sql -o generated/ --db-url clickhouse://localhost:8123

# Single file
chty generate queries/users.sql -o generated/ --db-url clickhouse://admin:admin@localhost:8123

# Parameter types only (fallback)
chty generate queries/*.sql -o generated/

# Custom output directory
chty generate src/sql/*.sql --output src/generated/
```

#### Connection URL Format

**Local ClickHouse:**
```
clickhouse://username:password@host:port[/database]
```

**ClickHouse Cloud:**
```
https://username:password@host:port[/database]
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

#### Output

For each `.sql` file, generates a `.py` file with:

- `{QueryName}Params` - Type-safe parameter class
- `{QueryName}Result` - TypedDict for results (with `--db-url`)
- `{QueryName}Query` - Query wrapper class (with `--db-url`)
- `QUERY` - The SQL query constant

---

### `chty validate`

Validate generated code against current ClickHouse schema.

```bash
chty validate [OPTIONS] GENERATED_FILES...
```

#### Arguments

- `GENERATED_FILES...` - One or more generated Python files to validate

#### Options

- `--db-url` `TEXT` - ClickHouse connection URL (required)

#### Examples

```bash
# Validate all generated files
chty validate generated/*.py --db-url clickhouse://localhost:8123

# Validate specific file
chty validate generated/users.py --db-url clickhouse://admin:admin@localhost:8123

# Use in CI
chty validate generated/*.py --db-url $CLICKHOUSE_URL
```

#### Exit Codes

- `0` - All files are valid
- `1` - One or more files failed validation

#### Validation Checks

- Missing columns in current schema
- Extra columns in current schema  
- Type mismatches between expected and actual types

---

## Global Options

### `--help`

Show help message and exit.

```bash
chty --help
chty generate --help
chty validate --help
```

### `--version`

Show version and exit.

```bash
chty --version
```

---

## Environment Variables

### `CLICKHOUSE_URL`

Set default connection URL:

```bash
export CLICKHOUSE_URL="clickhouse://admin:admin@localhost:8123"
chty generate queries/*.sql -o generated/ --db-url $CLICKHOUSE_URL
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (validation failed, generation error, etc.) |
| `2` | Invalid command line arguments |

---

## Tips

### Use Shell Completion

Install shell completion for better CLI experience:

```bash
chty --install-completion
```

### Glob Patterns

Use shell glob patterns to process multiple files:

```bash
# All SQL files
chty generate **/*.sql -o generated/ --db-url $DB_URL

# Specific pattern
chty generate queries/users_*.sql -o generated/ --db-url $DB_URL
```

### Makefile Integration

```makefile
.PHONY: generate validate

generate:
	chty generate queries/*.sql -o generated/ --db-url $(DB_URL)

validate:
	chty validate generated/*.py --db-url $(DB_URL)

all: generate validate
```

### CI/CD Integration

```yaml
# GitHub Actions
- name: Generate and validate
  run: |
    chty generate queries/*.sql -o generated/ --db-url ${{ secrets.DB_URL }}
    chty validate generated/*.py --db-url ${{ secrets.DB_URL }}
```

---

## See Also

- [Quick Start](../getting-started/quick-start.md)
- [Full Type Safety](../guide/full-type-safety.md)
- [Schema Validation](../guide/schema-validation.md)

