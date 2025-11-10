#!/bin/bash
# Quick start script for DeepSeek R1 Local Web UI

echo "======================================"
echo "DeepSeek R1 Local Web UI - Quick Start"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/.deps_installed" ]; then
    echo "Installing dependencies (this may take a few minutes)..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.deps_installed
    echo "Dependencies installed!"
fi

# Check if model is downloaded
if [ ! -d "models/deepseek-r1" ]; then
    echo ""
    echo "Model not found. Would you like to download it now?"
    echo "This will download approximately 3-4GB of data."
    read -p "Download model? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python download_model.py
    else
        echo "Please run 'python download_model.py' before starting the app."
        exit 1
    fi
fi

# Start the application
echo ""
echo "Starting DeepSeek R1 Web UI..."
python app.py
