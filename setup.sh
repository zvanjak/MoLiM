#!/bin/bash
# MoLiM Project Setup Script for Linux/Mac
# This script sets up the Python virtual environment and installs all dependencies

echo "Setting up MoLiM project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Display Python version
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully!"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "Installing project dependencies..."
python -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "Setup completed successfully!"
    echo ""
    echo "To activate the virtual environment in the future, run:"
    echo "  source .venv/bin/activate"
    echo ""
    echo "To run the project:"
    echo "  python MoLiM.py"
else
    echo ""
    echo "Error: Failed to install dependencies"
    exit 1
fi
