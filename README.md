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

4. Copy the env template and fill in API keys (see below):
```bash
cp .env.example .env
```

## API Keys

MoLiM is migrating from `cinemagoer` (broken by IMDb's anti-bot WAF) to a
hybrid OMDb + TMDb data layer (tracked in epic `MoLiM-02x`). Both APIs are
free and require accounts:

| Service | Used for | Sign up |
|---|---|---|
| **OMDb** | IMDb rating, votes, box office | http://www.omdbapi.com/apikey.aspx (free, 1,000 calls/day) |
| **TMDb** | Cast, crew, runtime, genres, posters | https://www.themoviedb.org/settings/api (free, requires attribution) |

Place your keys in a `.env` file at the project root (gitignored):

```
OMDB_API_KEY=your_omdb_key_here
TMDB_API_KEY=your_tmdb_key_here
```

These are loaded automatically via `config.py` (`from config import get_settings`).

> This product uses the TMDb API but is not endorsed or certified by TMDb.

## Running the Project

After setup, activate the virtual environment (if not already activated) and run:
```bash
python MoLiM.py
```

## Dependencies
- **cinemagoer** *(deprecated, scheduled for removal in MoLiM-dyy)* - Legacy IMDb access
- **requests** - HTTP client for OMDb / TMDb APIs
- **python-dotenv** - Loads API keys from `.env`
- **lxml**, **sqlalchemy** - Pulled in by cinemagoer (will go away with it)
