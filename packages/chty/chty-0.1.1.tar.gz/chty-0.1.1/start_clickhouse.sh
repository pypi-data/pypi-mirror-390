#!/bin/bash

docker run -d \
  --rm \
  --name clickhouse-server \
  -p 8123:8123 \
  -p 9000:9000 \
  -e CLICKHOUSE_USER=admin \
  -e CLICKHOUSE_PASSWORD=admin \
  clickhouse/clickhouse-server

