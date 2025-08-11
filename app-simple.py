import os
import sys

# Ensure the app directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
except ImportError as e:
    print(f"Import error: {e}")
    # Try to install the missing dependency
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask-Cors==6.0.1"])
    from app import app

# Export the app for gunicorn
app = app

if __name__ == "__main__":
    app.run()
