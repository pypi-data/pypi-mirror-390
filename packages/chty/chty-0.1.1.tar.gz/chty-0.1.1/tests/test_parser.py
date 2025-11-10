"""Tests for the SQL parser."""

from chty.parser import extract_parameters, QueryParameter


def test_extract_single_parameter():
    query = "SELECT * FROM users WHERE id = {user_id:Int32}"
    params = extract_parameters(query)

    assert len(params) == 1
    assert params[0].name == "user_id"
    assert params[0].clickhouse_type == "Int32"


def test_extract_multiple_parameters():
    query = """
        SELECT * FROM users 
        WHERE age >= {min_age:Int32} 
        AND name LIKE {pattern:String}
        AND created_at > {start_date:DateTime}
    """
    params = extract_parameters(query)

    assert len(params) == 3
    assert params[0].name == "min_age"
    assert params[0].clickhouse_type == "Int32"
    assert params[1].name == "pattern"
    assert params[1].clickhouse_type == "String"
    assert params[2].name == "start_date"
    assert params[2].clickhouse_type == "DateTime"


def test_extract_duplicate_parameters():
    query = """
        SELECT * FROM users 
        WHERE age >= {min_age:Int32}
        OR age <= {min_age:Int32}
    """
    params = extract_parameters(query)

    assert len(params) == 1
    assert params[0].name == "min_age"


def test_extract_complex_types():
    query = """
        SELECT * FROM users 
        WHERE tags IN {tag_list:Array(String)}
        AND score >= {min_score:Nullable(Float64)}
    """
    params = extract_parameters(query)

    assert len(params) == 2
    assert params[0].name == "tag_list"
    assert params[0].clickhouse_type == "Array(String)"
    assert params[1].name == "min_score"
    assert params[1].clickhouse_type == "Nullable(Float64)"


def test_extract_no_parameters():
    query = "SELECT * FROM users"
    params = extract_parameters(query)

    assert len(params) == 0

