# Examples

Real-world usage examples and patterns.

## Basic Query

=== "SQL"
    ```sql title="queries/users.sql"
    SELECT user_id, username, email
    FROM users
    WHERE age >= {min_age:Int32}
    LIMIT {limit:Int32}
    ```

=== "Python"
    ```python
    from generated.users import UsersParams, UsersQuery
    import clickhouse_connect

    client = clickhouse_connect.get_client(host="localhost")
    params = UsersParams(min_age=18, limit=10)
    query = UsersQuery(client)

    results = query.execute(params)
    for user in results:
        print(f"{user['username']}: {user['email']}")
    ```

## With Date/Time

=== "SQL"
    ```sql title="queries/events.sql"
    SELECT event_id, event_type, user_id, timestamp
    FROM events
    WHERE 
        timestamp >= {start_time:DateTime}
        AND timestamp < {end_time:DateTime}
        AND event_type = {type:String}
    ORDER BY timestamp DESC
    ```

=== "Python"
    ```python
    from datetime import datetime, timedelta
    from generated.events import EventsParams, EventsQuery
    import clickhouse_connect

    client = clickhouse_connect.get_client(host="localhost")
    
    params = EventsParams(
        start_time=datetime.now() - timedelta(days=7),
        end_time=datetime.now(),
        type="click"
    )
    query = EventsQuery(client)

    results = query.execute(params)
    for event in results:
        print(f"{event['timestamp']}: {event['event_type']}")
    ```

## Array Parameters

=== "SQL"
    ```sql title="queries/user_search.sql"
    SELECT user_id, username
    FROM users
    WHERE user_id IN {user_ids:Array(Int64)}
    ```

=== "Python"
    ```python
    from generated.user_search import UserSearchParams, UserSearchQuery
    import clickhouse_connect

    client = clickhouse_connect.get_client(host="localhost")
    
    params = UserSearchParams(user_ids=[1, 2, 3, 4, 5])
    query = UserSearchQuery(client)

    results = query.execute(params)
    ```

## Optional Parameters (Nullable)

=== "SQL"
    ```sql title="queries/filtered_users.sql"
    SELECT user_id, username, score
    FROM users
    WHERE score >= {min_score:Nullable(Float64)}
    ```

=== "Python"
    ```python
    from generated.filtered_users import FilteredUsersParams, FilteredUsersQuery
    import clickhouse_connect

    client = clickhouse_connect.get_client(host="localhost")
    
    # With value
    params = FilteredUsersParams(min_score=0.8)
    
    # Or None
    params = FilteredUsersParams(min_score=None)
    
    query = FilteredUsersQuery(client)
    results = query.execute(params)
    ```

## Complex Aggregation

=== "SQL"
    ```sql title="queries/user_stats.sql"
    SELECT 
        user_id,
        count() as event_count,
        uniq(session_id) as session_count,
        avg(duration) as avg_duration
    FROM events
    WHERE 
        timestamp >= {start_date:DateTime}
        AND user_id IN {user_ids:Array(Int64)}
    GROUP BY user_id
    HAVING event_count > {min_events:Int32}
    ```

=== "Python"
    ```python
    from datetime import datetime, timedelta
    from generated.user_stats import UserStatsParams, UserStatsQuery
    import clickhouse_connect

    client = clickhouse_connect.get_client(host="localhost")
    
    params = UserStatsParams(
        start_date=datetime.now() - timedelta(days=30),
        user_ids=[100, 200, 300],
        min_events=10
    )
    query = UserStatsQuery(client)

    results = query.execute(params)
    for stats in results:
        print(f"User {stats['user_id']}: {stats['event_count']} events")
    ```

## With ClickHouse Settings

Pass settings via `**kwargs`:

```python
results = query.execute(
    params,
    settings={
        'max_threads': 4,
        'max_execution_time': 30,
        'use_query_cache': 1
    }
)
```

## DataFrame Mode

Use `execute_df()` for DataFrame-based workflows:

```python
results = query.execute_df(params)

# Still typed as list[TypedDict]
for row in results:
    print(row['username'])  # Full autocomplete!
```

## With Validation

Enable runtime schema validation:

```python
query = UsersQuery(client, validate=True)

try:
    results = query.execute(params)
except ValueError as e:
    print(f"Schema mismatch: {e}")
    # Regenerate types!
```

## Multiple Queries

Organize multiple queries:

```python
from generated.users import UsersQuery
from generated.events import EventsQuery
from generated.products import ProductsQuery
import clickhouse_connect

client = clickhouse_connect.get_client(host="localhost")

# Initialize all queries
users = UsersQuery(client)
events = EventsQuery(client)
products = ProductsQuery(client)

# Use as needed
user_results = users.execute(user_params)
event_results = events.execute(event_params)
product_results = products.execute(product_params)
```

## Error Handling

```python
from clickhouse_connect.driver.exceptions import DatabaseError

try:
    results = query.execute(params)
except TypeError as e:
    print(f"Invalid parameters: {e}")
except ValueError as e:
    print(f"Schema mismatch: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## See Also

- [Quick Start](../getting-started/quick-start.md)
- [Full Type Safety](../guide/full-type-safety.md)
- [Type Mapping](type-mapping.md)

