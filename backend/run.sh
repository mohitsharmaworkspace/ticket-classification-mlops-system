#!/bin/bash

# Startup script for backend API

echo "=========================================="
echo "Ticket Classification API - Startup"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p ../logs
mkdir -p ../data/ground_truth
mkdir -p ../models/embeddings

# Run the API
echo "Starting API server..."
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "=========================================="

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Made with Bob
