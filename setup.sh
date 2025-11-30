#!/bin/bash
# MoLiM Project Setup Script
# Sets up Python 3.11 virtual environment and installs dependencies

echo "=== MoLiM Project Setup ==="
echo ""

# Check if Python 3.11 is available
echo "Checking for Python 3.11..."
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "✓ Found: $(python3.11 --version)"
elif command -v python3 &> /dev/null && [[ $(python3 --version) == *"3.11"* ]]; then
    PYTHON_CMD="python3"
    echo "✓ Found: $(python3 --version)"
else
    echo "✗ Python 3.11 not found!"
    echo ""
    echo "Please install Python 3.11:"
    echo "  Ubuntu/Debian: sudo apt install python3.11 python3.11-venv"
    echo "  macOS: brew install python@3.11"
    echo ""
    echo "Note: Python 3.14 is NOT compatible with cinemagoer library"
    exit 1
fi
echo ""

# Remove old virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf .venv
    echo "✓ Old .venv removed"
    echo ""
fi

# Create new virtual environment with Python 3.11
echo "Creating Python 3.11 virtual environment..."
$PYTHON_CMD -m venv .venv

if [ $? -ne 0 ]; then
    echo "✗ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Verify Python version
VENV_PYTHON=$(python --version)
echo "✓ Active Python: $VENV_PYTHON"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "✗ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Verify cinemagoer installation
echo "Verifying cinemagoer installation..."
python -c "from imdb import Cinemagoer; print('✓ cinemagoer imported successfully!')"

if [ $? -ne 0 ]; then
    echo "✗ cinemagoer import failed"
    exit 1
fi

echo ""

# Show installed packages
echo "=== Installed Packages ==="
pip list | grep -E "cinemagoer|pytest"
echo ""

# Final summary
echo "=== Setup Complete! ==="
echo ""
echo "Python version:"
python --version
echo ""
echo "Virtual environment: .venv (Python 3.11)"
echo "To activate: source .venv/bin/activate"
echo ""
echo "Ready to run tests:"
echo "  pytest tests/test_imdb_fetching.py -v"
echo ""
echo "Note: Always use Python 3.11 for this project!"
echo "      Python 3.14 is incompatible with cinemagoer"
