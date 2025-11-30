# MoLiM Project Setup Script
# Sets up Python 3.11 virtual environment and installs dependencies

Write-Host "=== MoLiM Project Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if Python 3.11 is available
Write-Host "Checking for Python 3.11..." -ForegroundColor Yellow
$python311 = py -3.11 --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Python 3.11 not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.11 from:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: Python 3.14 is NOT compatible with cinemagoer library" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Found: $python311" -ForegroundColor Green
Write-Host ""

# Remove old virtual environment if it exists
if (Test-Path ".venv") {
    Write-Host "Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .venv
    Write-Host "✓ Old .venv removed" -ForegroundColor Green
    Write-Host ""
}

# Create new virtual environment with Python 3.11
Write-Host "Creating Python 3.11 virtual environment..." -ForegroundColor Yellow
py -3.11 -m venv .venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Virtual environment created" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Verify Python version
$venvPython = python --version
Write-Host "✓ Active Python: $venvPython" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Verify cinemagoer installation
Write-Host "Verifying cinemagoer installation..." -ForegroundColor Yellow
python -c "from imdb import Cinemagoer; print('✓ cinemagoer imported successfully!')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ cinemagoer import failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Show installed packages
Write-Host "=== Installed Packages ===" -ForegroundColor Cyan
pip list | Select-String -Pattern "cinemagoer|pytest"
Write-Host ""

# Final summary
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Python version:" -ForegroundColor White
python --version
Write-Host ""
Write-Host "Virtual environment: .venv (Python 3.11)" -ForegroundColor White
Write-Host "To activate: .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "Ready to run tests:" -ForegroundColor White
Write-Host "  pytest tests/test_imdb_fetching.py -v" -ForegroundColor Gray
Write-Host ""
Write-Host "Note: Always use Python 3.11 for this project!" -ForegroundColor Yellow
Write-Host "      Python 3.14 is incompatible with cinemagoer" -ForegroundColor Yellow
