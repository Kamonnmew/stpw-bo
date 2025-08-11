import sys
import subprocess
import os

def install_package(package):
    """Install package if not already installed"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_dependencies():
    """Check and install required dependencies"""
    dependencies = [
        ("flask_cors", "Flask-Cors==4.0.1"),
        ("requests", "requests==2.31.0"),
        ("azure.search.documents", "azure-search-documents==11.4.0"),
        ("azure.storage.blob", "azure-storage-blob==12.19.0"),
        ("azure.core", "azure-core==1.28.0")
    ]
    
    # เช็ค python-dotenv แยกเพราะต้อง import แบบพิเศษ
    try:
        from dotenv import load_dotenv
        print("python-dotenv already installed")
    except ImportError:
        print("Installing python-dotenv...")
        install_package("python-dotenv==1.0.0")
    
    for module_name, package_spec in dependencies:
        try:
            __import__(module_name)
            print(f"{package_spec.split('==')[0]} already installed")
        except ImportError:
            print(f"Installing {package_spec}...")
            install_package(package_spec)

# เช็คและติดตั้ง dependencies ก่อน
check_and_install_dependencies()

# Import แอปหลัก
from app import app

# Export app สำหรับ gunicorn
app = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
