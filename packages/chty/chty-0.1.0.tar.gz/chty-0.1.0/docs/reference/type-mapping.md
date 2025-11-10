# Type Mapping Reference

Complete reference for how ClickHouse types map to Python types in generated code.

## Basic Types

| ClickHouse Type | Python Type | Example Value |
|----------------|-------------|---------------|
| `Int8`, `Int16`, `Int32`, `Int64` | `int` | `42` |
| `Int128`, `Int256` | `int` | `12345...` |
| `UInt8`, `UInt16`, `UInt32`, `UInt64` | `int` | `100` |
| `UInt128`, `UInt256` | `int` | `99999...` |
| `Float32`, `Float64` | `float` | `3.14` |
| `String` | `str` | `"hello"` |
| `FixedString(N)` | `str` | `"fixed"` |
| `Bool` | `bool` | `True` |
| `UUID` | `str` | `"550e8400-..."` |

## Date and Time Types

| ClickHouse Type | Python Type | Import Required | Example |
|----------------|-------------|----------------|---------|
| `Date` | `date` | `from datetime import date` | `date(2024, 1, 1)` |
| `Date32` | `date` | `from datetime import date` | `date(2024, 1, 1)` |
| `DateTime` | `datetime` | `from datetime import datetime` | `datetime(2024, 1, 1, 12, 0)` |
| `DateTime64(precision)` | `datetime` | `from datetime import datetime` | `datetime(2024, 1, 1, 12, 0, 0, 123456)` |

## Decimal Types

| ClickHouse Type | Python Type | Notes |
|----------------|-------------|-------|
| `Decimal(P, S)` | `float` | Precision/scale not preserved |
| `Decimal32(S)` | `float` | |
| `Decimal64(S)` | `float` | |
| `Decimal128(S)` | `float` | |
| `Decimal256(S)` | `float` | |

!!! note "Decimal Handling"
    Decimals map to `float` for simplicity. For precise decimal arithmetic, consider post-processing with Python's `decimal.Decimal`.

## Container Types

### Nullable

Makes any type optional:

| ClickHouse Type | Python Type |
|----------------|-------------|
| `Nullable(Int32)` | `int \| None` |
| `Nullable(String)` | `str \| None` |
| `Nullable(DateTime)` | `datetime \| None` |

Example:
```python
score: int | None  # From Nullable(Int32)
```

### Array

Homogeneous lists:

| ClickHouse Type | Python Type |
|----------------|-------------|
| `Array(Int32)` | `list[int]` |
| `Array(String)` | `list[str]` |
| `Array(Array(Int32))` | `list[list[int]]` |

Example:
```python
tags: list[str]  # From Array(String)
matrix: list[list[int]]  # From Array(Array(Int32))
```

### Map

Key-value mappings:

| ClickHouse Type | Python Type |
|----------------|-------------|
| `Map(String, Int32)` | `dict[str, int]` |
| `Map(Int32, String)` | `dict[int, str]` |
| `Map(String, Array(Int32))` | `dict[str, list[int]]` |

Example:
```python
scores: dict[str, int]  # From Map(String, Int32)
```

### Tuple

Fixed-size heterogeneous tuples:

| ClickHouse Type | Python Type |
|----------------|-------------|
| `Tuple(Int32, String)` | `tuple[int, str]` |
| `Tuple(String, Float64, Bool)` | `tuple[str, float, bool]` |

Example:
```python
point: tuple[float, float]  # From Tuple(Float64, Float64)
```

## Complex Examples

### Nested Containers

```python
# Array(Nullable(String))
optional_tags: list[str | None]

# Map(String, Array(Int32))
tag_scores: dict[str, list[int]]

# Nullable(Array(String))
maybe_tags: list[str] | None

# Array(Tuple(String, Int32))
entries: list[tuple[str, int]]
```

### Real-World Examples

```sql
-- Query with complex types
SELECT
    user_id,                                    -- Int64 → int
    username,                                   -- String → str
    email,                                      -- Nullable(String) → str | None
    created_at,                                 -- DateTime → datetime
    tags,                                       -- Array(String) → list[str]
    metadata,                                   -- Map(String, String) → dict[str, str]
    scores                                      -- Array(Float64) → list[float]
FROM users
```

Generated TypedDict:
```python
class UsersResult(TypedDict):
    user_id: int
    username: str
    email: str | None
    created_at: datetime
    tags: list[str]
    metadata: dict[str, str]
    scores: list[float]
```

## Unsupported Types

Some ClickHouse types don't have direct Python equivalents and map to `Any`:

- `Enum8`, `Enum16` - Maps to underlying integer type or `Any`
- `Nested` - Maps to `Any` (complex structure)
- `IPv4`, `IPv6` - Maps to `str` or `Any`
- `LowCardinality(T)` - Maps to underlying type `T`
- Custom aggregation states - Maps to `Any`

When a type maps to `Any`, you'll see:

```python
from typing import Any

some_field: Any  # Unsupported ClickHouse type
```

## Type Coercion

### Parameters (Input)

The generated parameter class validates types at construction:

```python
params = UsersParams(
    user_id=123,              # ✓ int
    username="john",          # ✓ str
    created_at=datetime.now() # ✓ datetime
)

params = UsersParams(
    user_id="not an int"      # ✗ TypeError at runtime
)
```

### Results (Output)

Results are returned as dictionaries. Python's type system doesn't enforce TypedDict at runtime:

```python
results = query.execute(params)
# results: list[UsersResult]

for user in results:
    user['user_id']  # Runtime: dict access
    # But type checker knows it exists and is an int
```

## Custom Type Handling

For types that need custom handling:

### Option 1: Post-process

```python
from decimal import Decimal

results = query.execute(params)
for row in results:
    # Convert float to Decimal
    precise_amount = Decimal(str(row['amount']))
```

### Option 2: Type Assertion

```python
from typing import cast

results = query.execute(params)
for row in results:
    # Assert more specific type
    user_id = cast(int, row['user_id'])
```

## See Also

- [Full Type Safety](../guide/full-type-safety.md) - How type safety works
- [Basic Usage](../getting-started/basic-usage.md) - Using generated types
- [CLI Reference](cli.md) - Generation commands

