import sys
import subprocess
import os

def install_if_missing(module_name, package_name):
    """Install package if module not found"""
    try:
        __import__(module_name)
    except ImportError:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# ติดตั้ง dependencies ที่จำเป็น
install_if_missing("flask_cors", "Flask-Cors==4.0.1")
install_if_missing("requests", "requests==2.31.0")
install_if_missing("azure.core", "azure-core==1.30.0")
install_if_missing("azure.common", "azure-common==1.1.28")
install_if_missing("azure.search.documents", "azure-search-documents==11.4.0")
install_if_missing("azure.storage.blob", "azure-storage-blob==12.19.0")

# เช็ค python-dotenv แบบพิเศษ (ตาม ImageSearch.py)
try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing python-dotenv...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv==1.0.0"])

# Import app
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
