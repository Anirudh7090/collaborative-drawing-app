#!/usr/bin/env bash
pip install --upgrade pip
cd project-root/backend
pip install -r requirements.txt
python app/init_db.py
