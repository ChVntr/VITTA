#!/bin/bash

pip install -r requirements.txt

FILE="/__pycache__/"

if [ -f "instance/vitta.db" ]; then
    echo "vitta.db exists."
else
    flask --app app init-db
fi

flask --app app create-admin
flask --app app seed-db
flask --app app run --debug