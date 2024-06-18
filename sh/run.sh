#!/bin/bash
#you should use sudo to run this script
# 獲取腳本所在的目錄
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# 進入腳本所在的目錄
cd "$SCRIPT_DIR"

sh docker-db.sh
cd ..

cd api 
rm -f .env
cp ../.env .
# pipenv install uvicorn 
# pipenv install -r requirements.txt
bash api.sh &

cd ../main-controller
rm -f .env
cp ../.env .
# pipenv install -r requirements.txt
pipenv run python3 main-controller.py
