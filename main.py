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

def install_batch_packages():
    """Install all required packages in one go if any missing"""
    packages_to_install = []
    
    # Check each module
    try:
        import flask_cors
    except ImportError:
        packages_to_install.append("Flask-Cors==4.0.1")
    
    try:
        import requests
    except ImportError:
        packages_to_install.append("requests==2.32.4")
        
    try:
        import azure.core
    except ImportError:
        packages_to_install.append("azure-core==1.35.0")
        
    try:
        import azure.common
    except ImportError:
        packages_to_install.append("azure-common==1.1.28")
        
    try:
        import azure.search.documents
    except ImportError:
        packages_to_install.append("azure-search-documents==11.4.0b11")
        
    try:
        import azure.storage.blob
    except ImportError:
        packages_to_install.append("azure-storage-blob==12.26.0")
    
    try:
        from dotenv import load_dotenv
    except ImportError:
        packages_to_install.append("python-dotenv==1.1.1")
    
    # Install all missing packages at once
    if packages_to_install:
        print(f"Installing packages: {', '.join(packages_to_install)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages_to_install)

# Install dependencies efficiently
install_batch_packages()

# Import app
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
