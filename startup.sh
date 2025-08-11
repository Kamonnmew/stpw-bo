#!/bin/bash
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt
echo "Starting application with gunicorn..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 app:app