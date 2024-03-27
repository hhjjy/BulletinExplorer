#!/bin/bash
source ../.env
HOST=$API_DEV_HOST
PORT=$API_DEV_PORT
MODE="DEVELOPMENT"

# 檢查 環境變數不分大小寫 
if [[ "${DEV_OR_MAIN,,}" = "main" ]]; then
    echo "MAIN MODE"
    HOST=$API_MAIN_HOST
    PORT=$API_MAIN_PORT
    MODE="MAIN"
elif [[ "${DEV_OR_MAIN,,}" = "dev" ]]; then
    echo "DEVELOPMENT MODE"
else
    echo "Unrecognized mode: $DEV_OR_MAIN. Defaulting to DEVELOPMENT MODE."
fi

cd ../api

# 启动服务!
echo "Starting API in $MODE mode at $HOST on port $PORT"
uvicorn api:app --host $HOST --port $PORT --reload
