# MoLiM - Movie Library Manager

A Python application for managing and organizing a movie library with
IMDb metadata integration.

## Requirements

- **Python 3.11 or newer** (3.11, 3.12, 3.13, 3.14 all supported)
- An OMDb API key and a TMDb API key (both free)

## Quick Setup

### Windows
```powershell
.\setup.ps1
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

```bash
python -m venv .venv
# Activate:
#   Windows PowerShell: .\.venv\Scripts\Activate.ps1
#   Windows CMD:        .venv\Scripts\activate.bat
#   Linux/Mac:          source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit .env with your API keys
```

## API Keys

The IMDb data layer is a hybrid OMDb + TMDb client (epic `MoLiM-02x`).
Both APIs are free; both require accounts:

| Service | Used for | Sign up |
|---|---|---|
| **OMDb** | IMDb rating, votes, box office, country, language | http://www.omdbapi.com/apikey.aspx (free, 1,000 calls/day) |
| **TMDb** | Cast, crew, runtime, genres, posters | https://www.themoviedb.org/settings/api (free, requires attribution) |

Place your keys in a `.env` file at the project root (gitignored):

```
OMDB_API_KEY=your_omdb_key_here
TMDB_API_KEY=your_tmdb_key_here
```

These are loaded automatically via `config.py` (`from config import get_settings`).

> This product uses the TMDb API but is not endorsed or certified by TMDb.

## Running the Project

After setup, activate the virtual environment and run:

```bash
python MoLiM.py
```

The `MoLiM.py` entry point currently runs `processing.processFolder(<path>)`
on a hard-coded folder; edit it to point at your own backlog.

## Caching

OMDb + TMDb responses are cached as JSON files under `./cache/` keyed
by IMDb tt-ID, with a 30-day TTL. Re-running the pipeline on the same
titles is fast and saves API quota. The `cache/` directory is gitignored;
delete it any time to force a refresh.

## Dependencies

- **requests** - HTTP client for OMDb / TMDb APIs
- **python-dotenv** - Loads API keys from `.env`
- **pytest**, **pytest-cov**, **pytest-mock** - Test stack
