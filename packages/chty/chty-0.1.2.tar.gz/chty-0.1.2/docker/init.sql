-- Initialize database schema for chty examples

CREATE DATABASE IF NOT EXISTS default;

CREATE TABLE IF NOT EXISTS default.users (
    user_id Int64,
    username String,
    email String,
    age Int32,
    created_at DateTime,
    tags Array(String),
    metadata String,
    is_active Bool,
    score Nullable(Float64)
) ENGINE = MergeTree()
ORDER BY user_id;

-- Insert sample data for testing
INSERT INTO default.users VALUES
    (1, 'john_doe', 'john@example.com', 25, '2020-01-15 10:30:00', ['python', 'clickhouse'], '{"role": "developer"}', true, 0.95),
    (2, 'jane_smith', 'jane@example.com', 30, '2019-06-20 14:45:00', ['sql', 'database'], '{"role": "dba"}', true, 0.88),
    (3, 'bob_johnson', 'bob@example.com', 22, '2021-03-10 09:15:00', ['python', 'data'], '{"role": "analyst"}', false, 0.72),
    (4, 'alice_wong', 'alice@example.com', 28, '2020-08-05 16:20:00', ['clickhouse', 'database', 'python'], '{"role": "engineer"}', true, 0.91),
    (5, 'charlie_brown', 'charlie@example.com', 35, '2018-11-12 11:00:00', ['admin'], '{"role": "admin"}', true, NULL);

