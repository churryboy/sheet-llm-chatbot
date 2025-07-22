#!/usr/bin/env python3
"""
Simple script to run the Flask server from the project root
"""
import os
import sys

# Change to backend directory
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)

# Add backend to Python path
sys.path.insert(0, backend_dir)

# Import and run the app
from app import app
app.run(debug=True, port=8000, threaded=True)
