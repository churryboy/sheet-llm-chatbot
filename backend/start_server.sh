#!/bin/bash

# Kill any existing process on port 5001
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Navigate to backend directory
cd /Users/churryboy/sheet-llm-chatbot/backend

# Activate virtual environment
source venv/bin/activate

# Start the server
echo "Starting Flask server on port 5001..."
python app.py
