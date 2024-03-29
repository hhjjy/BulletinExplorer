#!/bin/bash

sh docker-db.sh
cd ..

cd api 
rm -f .env
cp ../.env .
pipenv install uvicorn 
pipenv install -r requirements.txt
bash api.sh &




cd ../main-controller
rm -f .env
cp ../.env .
pipenv install -r requirements.txt
pipenv run python3 main-controller.py
