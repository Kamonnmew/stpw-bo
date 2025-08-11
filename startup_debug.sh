#!/bin/bash

# === AZURE APP SERVICE STARTUP SCRIPT WITH FULL DEBUGGING ===
echo "=========================================="
echo "🚀 STARTUP DEBUG LOG - $(date)"
echo "=========================================="

# Set strict error handling
set -e
set -x

# Show environment
echo "📍 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version 2>&1 || echo 'Python not found')"
echo "📦 Pip version: $(pip --version 2>&1 || echo 'Pip not found')"
echo "🌍 Environment variables:"
env | grep -E "(WEBSITE_|PORT|PYTHONPATH)" || echo "No Azure env vars found"

# Ensure correct directory
cd /home/site/wwwroot || {
    echo "❌ FATAL: Cannot cd to /home/site/wwwroot"
    exit 1
}

# Set Python path
export PYTHONPATH="/home/site/wwwroot:${PYTHONPATH:-}"
echo "🐍 PYTHONPATH set to: $PYTHONPATH"

# Check critical files exist
echo "📋 Checking critical files:"
for file in main.py app.py requirements.txt; do
    if [[ -f "$file" ]]; then
        echo "✅ $file exists"
    else
        echo "❌ $file MISSING!"
        ls -la
        exit 1
    fi
done

# Install requirements
echo "📦 Installing requirements..."
python -m pip install --no-cache-dir --upgrade pip || echo "⚠️ Pip upgrade failed"
python -m pip install --no-cache-dir -r requirements.txt || {
    echo "❌ Requirements installation failed!"
    cat requirements.txt
    exit 1
}

# Test application import
echo "🧪 Testing application import..."
python -c "
import sys
sys.path.insert(0, '/home/site/wwwroot')
try:
    from main import application
    print('✅ Application import successful!')
    print(f'   Type: {type(application)}')
    print(f'   Name: {application.name}')
    
    # Test health endpoint
    with application.test_client() as client:
        response = client.get('/health')
        print(f'✅ Health check: {response.status_code} - {response.get_json()}')
        
except Exception as e:
    print(f'❌ Application import failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

echo "🚀 Starting Gunicorn with full logging..."

# Start Gunicorn with comprehensive logging
exec gunicorn \
    --bind=0.0.0.0:${PORT:-8000} \
    --workers=1 \
    --worker-class=sync \
    --timeout=600 \
    --graceful-timeout=60 \
    --keep-alive=5 \
    --max-requests=500 \
    --max-requests-jitter=50 \
    --preload \
    --access-logfile='-' \
    --error-logfile='-' \
    --log-level=debug \
    --capture-output \
    main:application

echo "❌ Gunicorn exited unexpectedly!"
