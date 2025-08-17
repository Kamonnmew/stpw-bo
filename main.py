#!/usr/bin/env python3
"""
Azure App Service Entry Point with Complete Error Handling
"""

import sys
import os
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

def install_if_missing(module_name, package_name):
    """Install package if module not found"""
    try:
        __import__(module_name)
        logger.info(f"✅ Module {module_name} already available")
    except ImportError:
        logger.info(f"📦 Installing {package_name}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--no-cache-dir", package_name
            ])
            logger.info(f"✅ Successfully installed {package_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install {package_name}: {e}")
            raise

def install_batch_packages():
    """Install all required packages in one go if any missing"""
    logger.info("🔍 Checking required packages...")
    
    packages_to_install = []
    required_packages = [
        ("flask", "Flask==3.1.1"),
        ("flask_cors", "Flask-Cors==6.0.1"), 
        ("requests", "requests==2.32.4"),
        ("azure.core", "azure-core==1.35.0"),
        ("azure.common", "azure-common==1.1.28"),
        ("azure.search.documents", "azure-search-documents==11.4.0b11"),
        ("azure.storage.blob", "azure-storage-blob==12.26.0"),
        ("dotenv", "python-dotenv==1.1.1"),
    ]
    
    for module_name, package_name in required_packages:
        try:
            if module_name == "dotenv":
                from dotenv import load_dotenv
            else:
                __import__(module_name)
            logger.info(f"✅ {module_name}: OK")
        except ImportError:
            logger.info(f"📦 {module_name}: MISSING - will install {package_name}")
            packages_to_install.append(package_name)
    
    # Install all missing packages at once
    if packages_to_install:
        logger.info(f"📦 Installing packages: {', '.join(packages_to_install)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--no-cache-dir"
            ] + packages_to_install)
            logger.info("✅ All packages installed successfully!")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Package installation failed: {e}")
            raise
    else:
        logger.info("✅ All required packages already available")

# Install dependencies with full error handling
try:
    logger.info("🚀 Starting application initialization...")
    install_batch_packages()
    logger.info("✅ Dependencies check completed")
except Exception as e:
    logger.error(f"❌ FATAL: Dependency installation failed: {e}")
    sys.exit(1)

# Import Flask app with error handling
try:
    logger.info("📱 Importing Flask application...")
    from app import app
    logger.info("✅ Flask app imported successfully")
    
    # Verify app routes
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    logger.info(f"📍 Available routes: {routes}")
    
except ImportError as e:
    logger.error(f"❌ FATAL: Cannot import Flask app: {e}")
    logger.error("Current directory contents:")
    try:
        import os
        for item in os.listdir('.'):
            logger.error(f"  - {item}")
    except:
        pass
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ FATAL: Unexpected error importing app: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)

# Create WSGI application object
try:
    application = app
    logger.info("✅ WSGI application object created")
    logger.info(f"   Type: {type(application)}")
    logger.info(f"   Name: {application.name}")
    
    # Test health endpoint
    with application.test_client() as client:
        response = client.get('/health')
        if response.status_code == 200:
            logger.info(f"✅ Health check passed: {response.get_json()}")
        else:
            logger.warning(f"⚠️ Health check returned: {response.status_code}")
            
except Exception as e:
    logger.error(f"❌ FATAL: Cannot create application object: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)

# Handle different execution contexts
if __name__ == "__main__":
    # Direct execution (development)
    logger.info("🔧 Running in DEVELOPMENT mode")
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting development server on port {port}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"❌ Development server failed: {e}")
        sys.exit(1)
else:
    # WSGI server import (production)
    logger.info("🏭 Running in PRODUCTION mode (WSGI)")
    logger.info("✅ Application ready for WSGI server")

# Export for external access
__all__ = ['application', 'app']
