#!/bin/bash
# 加载环境变量
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# 進入腳本所在的目錄
cd "$SCRIPT_DIR"
. ../.env

docker stop postgres-main
docker stop postgres-dev
docker rm postgres-main
docker rm postgres-dev

# # 创建数据目录
mkdir -p "${HOST_DIR}/main_data"
mkdir -p "${HOST_DIR}/dev_data"

# # 运行主环境数据库容器
docker run --name postgres-main \
  -e POSTGRES_DB=$POSTGRES_MAIN_DB \
  -e POSTGRES_USER=$POSTGRES_MAIN_USER \
  -e POSTGRES_PASSWORD=$POSTGRES_MAIN_PASSWORD \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -d -p $POSTGRES_MAIN_PORT:5432 \
  -v "${HOST_DIR}/main_data:/var/lib/postgresql/data" \
  -v "$(pwd)/mydb_schema.sql:/docker-entrypoint-initdb.d/mydb_schema.sql" \
  postgres

# # 运行开发环境数据库容器
docker run --name postgres-dev \
  -e POSTGRES_DB=$POSTGRES_DEV_DB \
  -e POSTGRES_USER=$POSTGRES_DEV_USER \
  -e POSTGRES_PASSWORD=$POSTGRES_DEV_PASSWORD \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -d -p $POSTGRES_DEV_PORT:5432 \
  -v "${HOST_DIR}/dev_data:/var/lib/postgresql/data" \
  -v "$(pwd)/mydb_schema.sql:/docker-entrypoint-initdb.d/mydb_schema.sql" \
  postgres


# psql -h localhost -p 65432 -U admin -d mydb
