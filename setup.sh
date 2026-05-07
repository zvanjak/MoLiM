#!/bin/bash
# MoLiM Project Setup Script
#
# Creates a .venv using the best available Python (>= 3.11) and
# installs requirements. As of MoLiM-dyy cinemagoer is gone, so the
# Python 3.11 ceiling is lifted - 3.11, 3.12, 3.13, 3.14 all work.

set -e

echo "=== MoLiM Project Setup ==="
echo ""

# Pick a Python interpreter (3.13 -> 3.12 -> 3.11 -> python3 -> python)
PYTHON_CMD=""
for cand in python3.13 python3.12 python3.11 python3 python; do
    if command -v "$cand" &> /dev/null; then
        ver=$("$cand" -c 'import sys;print("%d.%d"%sys.version_info[:2])')
        major=${ver%%.*}
        minor=${ver#*.}
        if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
            PYTHON_CMD="$cand"
            echo "✓ Found: $($cand --version)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "✗ No suitable Python (>= 3.11) found"
    echo "  Ubuntu/Debian: sudo apt install python3.12 python3.12-venv"
    echo "  macOS:         brew install python@3.12"
    exit 1
fi
echo ""

if [ -d ".venv" ]; then
    echo "Removing old .venv..."
    rm -rf .venv
    echo "✓ Removed"
    echo ""
fi

echo "Creating virtual environment..."
"$PYTHON_CMD" -m venv .venv
echo "✓ .venv created"
echo ""

# shellcheck disable=SC1091
source .venv/bin/activate
echo "✓ Active Python: $(python --version)"
echo ""

echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

echo "Configuring API keys..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ .env created from template"
    else
        echo "⚠ .env.example not found - skipping"
    fi
else
    echo "✓ .env already present"
fi
echo "  Edit .env and add:"
echo "    OMDB_API_KEY  - http://www.omdbapi.com/apikey.aspx"
echo "    TMDB_API_KEY  - https://www.themoviedb.org/settings/api"
echo ""

python -c "import config; s = config.get_settings(); print('OMDb:', 'set' if s.omdb_api_key else 'MISSING'); print('TMDb:', 'set' if s.tmdb_api_key else 'MISSING')"
echo ""

echo "=== Setup Complete! ==="
echo "Activate later with: source .venv/bin/activate"
echo "Run tests with:      pytest"
