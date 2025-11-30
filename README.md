# MoLiM - Movie Library Manager

A Python application for managing and organizing a movie library with IMDb metadata integration.

## ⚠️ Important: Python Version Requirement

**This project requires Python 3.11**

❌ **Python 3.14 is NOT compatible** - The `cinemagoer` library uses `pkgutil.find_loader` which was removed in Python 3.14.

## Quick Setup

### Windows
Run the setup script in PowerShell:
```powershell
.\setup.ps1
```

### Linux/Mac
Run the setup script in your terminal:
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup
If you prefer to set up manually:

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
   - **Windows PowerShell**: `.\.venv\Scripts\Activate.ps1`
   - **Windows CMD**: `.venv\Scripts\activate.bat`
   - **Linux/Mac**: `source .venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Project

After setup, activate the virtual environment (if not already activated) and run:
```bash
python MoLiM.py
```

## Dependencies
- **cinemagoer** (formerly IMDbPY) - For accessing IMDb data
- **lxml** - XML/HTML parser
- **sqlalchemy** - Database toolkit
