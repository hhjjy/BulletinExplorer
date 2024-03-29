#!/bin/bash

sh docker-db.sh
cd ..

cd api 
pipenv install uvicorn 
pipenv install -r requirements.txt
cd ../sh
bash api.sh &




cd ../main-controller
pipenv install -r requirements.txt
cd ..
pipenv run python3 main-controller/main-controller.py
