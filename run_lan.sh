#!/bin/bash
python3 -m venv ./venv
source venv/bin/activate
FLASK_APP=main.py flask run --host=0.0.0.0 --port=$1
deactivate
