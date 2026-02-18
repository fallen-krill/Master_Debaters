#!/bin/bash
python3 -m venv ./venv
source venv/bin/activate
DEBUG=1 python3 src/main.py
deactivate
