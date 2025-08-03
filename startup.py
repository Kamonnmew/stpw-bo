import os
import sys

# Add the site directory to Python path
site_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, site_dir)

from app import app

if __name__ == "__main__":
    app.run()
