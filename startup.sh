#!/bin/bash

# Ensure we're in the correct directory
cd /home/site/wwwroot

# Set Python path
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"

# Install any missing dependencies first
python -m pip install --no-cache-dir -r requirements.txt || echo "Requirements already satisfied"

# Start the application with proper configuration for Azure
exec gunicorn \
    --bind=0.0.0.0:8000 \
    --workers=2 \
    --worker-class=sync \
    --timeout=300 \
    --graceful-timeout=30 \
    --keep-alive=2 \
    --max-requests=1000 \
    --max-requests-jitter=100 \
    --preload \
    --access-logfile='-' \
    --error-logfile='-' \
    --log-level=info \
    main:application