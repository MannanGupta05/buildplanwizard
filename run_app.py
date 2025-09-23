"""
Flask application launcher for map approval system.
Run this file to start the web application.

Usage:
    python run_app.py
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the Flask app
from web.app import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)