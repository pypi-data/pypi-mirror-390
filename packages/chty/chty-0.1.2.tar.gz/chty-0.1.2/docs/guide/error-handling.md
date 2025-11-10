# Error Handling

Understanding and handling errors in `chty`.

## Error Categories

### 1. Development-Time Errors

Caught by type checkers (mypy, pyright):

```python
# ❌ Wrong parameter type
params = UsersParams(min_age="not a number")

# ❌ Missing parameter
params = UsersParams(min_age=18)  # Missing 'pattern'

# ❌ Unknown parameter
params = UsersParams(min_age=18, pattern="%test%", wrong=123)

# ❌ Wrong result field
row['usernam']  # Typo!
```

### 2. Runtime Errors

#### Parameter Errors

```python
try:
    params = UsersParams(min_age="invalid")
except TypeError as e:
    print(f"Invalid parameter type: {e}")
```

#### ClickHouse Query Errors

```python
try:
    results = query.execute(params)
except Exception as e:
    # ClickHouse exceptions propagate normally
    print(f"Query failed: {e}")
```

#### Schema Validation Errors

```python
query = UsersQuery(client, validate=True)

try:
    results = query.execute(params)
except ValueError as e:
    if "missing expected fields" in str(e):
        print("Schema mismatch - regenerate types!")
    elif "unexpected fields" in str(e):
        print("New fields added to schema")
```

### 3. Codegen Errors

#### No Parameters Found

```bash
$ chty generate queries/no_params.sql -o generated/

Processing queries/no_params.sql...
  ⚠️  No parameters found in queries/no_params.sql
```

**Solution:** Add parameters or skip the file.

#### Connection Error

```bash
$ chty generate queries/*.sql -o generated/ --db-url clickhouse://badhost:8123

Processing queries/users.sql...
  ✗ Error processing queries/users.sql: Connection refused
```

**Solution:** Check database URL and connectivity.

#### Invalid SQL

```bash
$ chty generate queries/bad.sql -o generated/ --db-url clickhouse://localhost:8123

Processing queries/bad.sql...
  ✗ Error processing queries/bad.sql: DB::Exception: Syntax error
```

**Solution:** Fix SQL syntax in the `.sql` file.

## Error Reference

| Error Type | When | Fix |
|-----------|------|-----|
| `TypeError` | Wrong param type | Check parameter types in call |
| `KeyError` | Wrong result field | Check TypedDict definition |
| `ValueError` | Schema mismatch (validate=True) | Regenerate types |
| `Exception` | ClickHouse query error | Check SQL, database state |
| CLI Exit 1 | Generation/validation failed | Check error message |

## Best Practices

### 1. Use Type Checkers

```bash
# Catch errors before running
mypy your_app.py
```

### 2. Handle ClickHouse Errors

```python
from clickhouse_connect.driver.exceptions import DatabaseError

try:
    results = query.execute(params)
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    # Handle gracefully
```

### 3. Validate in Development

```python
# Enable validation in dev/test only
is_dev = os.getenv("ENV") == "development"
query = UsersQuery(client, validate=is_dev)
```

### 4. Log Generation Errors

```bash
chty generate queries/*.sql -o generated/ --db-url $DB_URL 2>&1 | tee generation.log
```

### 5. Fail Fast in CI

```yaml
- name: Generate types
  run: |
    chty generate queries/*.sql -o generated/ --db-url $DB_URL
    # Exit code 1 fails the build
```

## See Also

- [Runtime Validation](runtime-validation.md)
- [Schema Validation](schema-validation.md)
- [CLI Reference](../reference/cli.md)

