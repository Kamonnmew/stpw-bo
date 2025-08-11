import sys
import subprocess

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# ติดตั้ง dependencies ที่จำเป็น
try:
    import flask_cors
except ImportError:
    print("Installing Flask-Cors...")
    install_package("Flask-Cors==4.0.1")
    import flask_cors

try:
    import requests
except ImportError:
    print("Installing requests...")
    install_package("requests==2.31.0")
    import requests

# Import แอปหลัก
from app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
