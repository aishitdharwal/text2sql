#!/bin/bash

# Backend startup script

echo "Starting Text2SQL Backend API..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and update with your credentials"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt --upgrade

# Run the application
echo "Starting FastAPI server on port 8080..."
python3 main.py
