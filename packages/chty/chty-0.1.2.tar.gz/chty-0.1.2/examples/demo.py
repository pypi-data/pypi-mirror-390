"""Demo of using chty-generated code with ClickHouse."""

import clickhouse_connect

CLICKHOUSE_USER = "admin"
CLICKHOUSE_PASSWORD = "admin"


def demo_simple_query():
    """Demonstrate the simple query example with typed results."""
    try:
        from examples.generated.simple import SimpleParams, SimpleQuery

        client = clickhouse_connect.get_client(
            host="localhost",
            port=8123,
            username=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
        )

        params = SimpleParams(multiplier=3, limit=5)
        query = SimpleQuery(client)

        # Execute using standard query method
        results = query.execute(params)
        print("Typed query results:")
        for row in results:
            print(f"  number={row['number']}, result={row['result']}")
        print()

        # Can also use execute_df for DataFrame-based execution
        results_df = query.execute_df(params)
        print(f"DataFrame results: {len(results_df)} rows")
        print()

    except ImportError:
        print(
            "Generate types first:\n"
            "  chty generate examples/queries/ -o examples/generated/ --db-url clickhouse://admin:admin@localhost:8123"
        )
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This requires a running ClickHouse server")


def demo_user_search():
    """Demonstrate the user search query with multiple parameters."""
    try:
        from datetime import datetime

        from examples.generated.user_search import QUERY, UserSearchParams

        params = UserSearchParams(
            search_pattern="%john%",
            min_age=18,
            start_date=datetime(2020, 1, 1),
            max_results=10,
        )

        print(f"Query: {QUERY}")
        print(f"Parameters: {params}")
        print()

    except ImportError:
        print(
            "Generate types first: chty generate examples/queries/ -o examples/generated/"
        )


def demo_complex_types():
    """Demonstrate complex type handling."""
    try:
        from examples.generated.complex_types import QUERY, ComplexTypesParams

        params = ComplexTypesParams(
            user_id=12345,
            tag_list=["python", "clickhouse", "database"],
            is_active=True,
            min_score=0.75,
        )

        print(f"Query: {QUERY}")
        print(f"Parameters: {params}")
        print()

    except ImportError:
        print(
            "Generate types first: chty generate examples/queries/ -o examples/generated/"
        )


if __name__ == "__main__":
    print("=== chty Demo ===\n")
    demo_simple_query()
    demo_user_search()
    demo_complex_types()
