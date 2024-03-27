#!/bin/sh
. ./.env
docker rm "$POSTGRES_DB"
docker run \
  --name $POSTGRES_DB \
  -v $HOST_DIR:/var/lib/postgresql/data \
  -v $(pwd)/mydb_schema.sql:/docker-entrypoint-initdb.d/mydb_schema.sql \
  -e POSTGRES_DB=$POSTGRES_DB \
  -e POSTGRES_USER=$POSTGRES_USER \
  -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  --expose 5432 \
  -p $POSTGRES_PORT:5432 \
   \
  postgres:latest \
  &
psql -h localhost -d $POSTGRES_DB -U $POSTGRES_USER -p $POSTGRES_PORT
