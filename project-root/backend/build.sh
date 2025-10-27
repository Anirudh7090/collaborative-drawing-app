#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Add the backend directory to PYTHONPATH so Python can find the 'app' module
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

python app/init_db.py
