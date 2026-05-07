# MoLiM Project Setup Script (Windows / PowerShell)
#
# Creates a .venv using the best available Python (>= 3.11) and
# installs requirements. As of MoLiM-dyy cinemagoer is gone, so the
# Python 3.11 ceiling is lifted - 3.11, 3.12, 3.13, 3.14 all work.

param(
    [string]$PythonVersion = ""
)

Write-Host "=== MoLiM Project Setup ===" -ForegroundColor Cyan
Write-Host ""

# Pick a Python interpreter
function Resolve-Python {
    param([string]$Pref)
    if ($Pref) {
        $v = & py "-$Pref" --version 2>$null
        if ($LASTEXITCODE -eq 0) { return @{ Cmd = "py"; Arg = "-$Pref"; Version = $v } }
        Write-Host "✗ Requested Python $Pref not found via 'py' launcher" -ForegroundColor Red
        exit 1
    }
    foreach ($cand in @("3.13", "3.12", "3.11")) {
        $v = & py "-$cand" --version 2>$null
        if ($LASTEXITCODE -eq 0) { return @{ Cmd = "py"; Arg = "-$cand"; Version = $v } }
    }
    $v = & python --version 2>$null
    if ($LASTEXITCODE -eq 0) { return @{ Cmd = "python"; Arg = $null; Version = $v } }
    return $null
}

$py = Resolve-Python -Pref $PythonVersion
if (-not $py) {
    Write-Host "✗ No suitable Python (>= 3.11) found" -ForegroundColor Red
    Write-Host "  Install from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Found: $($py.Version)" -ForegroundColor Green
Write-Host ""

if (Test-Path ".venv") {
    Write-Host "Removing old .venv..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .venv
    Write-Host "✓ Removed" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if ($py.Arg) {
    & $py.Cmd $py.Arg -m venv .venv
} else {
    & $py.Cmd -m venv .venv
}
if ($LASTEXITCODE -ne 0) { Write-Host "✗ venv creation failed" -ForegroundColor Red; exit 1 }
Write-Host "✓ .venv created" -ForegroundColor Green
Write-Host ""

& .\.venv\Scripts\Activate.ps1
Write-Host "✓ Active Python: $(python --version)" -ForegroundColor Green
Write-Host ""

Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Host "✗ install failed" -ForegroundColor Red; exit 1 }
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

Write-Host "Configuring API keys..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ .env created from template" -ForegroundColor Green
    } else {
        Write-Host "⚠ .env.example not found - skipping" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ .env already present" -ForegroundColor Green
}
Write-Host "  Edit .env and add:" -ForegroundColor Gray
Write-Host "    OMDB_API_KEY  - http://www.omdbapi.com/apikey.aspx" -ForegroundColor Gray
Write-Host "    TMDB_API_KEY  - https://www.themoviedb.org/settings/api" -ForegroundColor Gray
Write-Host ""

python -c "import config; s = config.get_settings(); print('OMDb:', 'set' if s.omdb_api_key else 'MISSING'); print('TMDb:', 'set' if s.tmdb_api_key else 'MISSING')"
Write-Host ""

Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host "Activate later with: .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "Run tests with:      pytest" -ForegroundColor Gray
