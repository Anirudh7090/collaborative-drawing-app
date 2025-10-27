#!/usr/bin/env bash
pip install --upgrade pip
pip install -r backend/requirements.txt
cd backend
python app/init_db.py
