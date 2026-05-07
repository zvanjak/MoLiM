"""Application configuration (MoLiM-1n6).

Loads API keys and runtime settings from environment variables. If a `.env`
file is present in the project root, `python-dotenv` is used to populate
`os.environ` from it before reading. `.env` is gitignored - copy
`.env.example` and fill in your keys.

Required keys (see https://www.omdbapi.com/apikey.aspx and
https://www.themoviedb.org/settings/api):

    OMDB_API_KEY
    TMDB_API_KEY

Usage:
    from config import get_settings
    settings = get_settings()
    settings.require_api_keys()  # raises ConfigError if missing
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

try:
    from dotenv import load_dotenv as _load_dotenv
except ImportError:  # python-dotenv not installed yet (pre-setup)
    _load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


@dataclass(frozen=True)
class Settings:
    omdb_api_key: str
    tmdb_api_key: str

    def require_api_keys(self) -> None:
        missing = []
        if not self.omdb_api_key:
            missing.append("OMDB_API_KEY")
        if not self.tmdb_api_key:
            missing.append("TMDB_API_KEY")
        if missing:
            raise ConfigError(
                "Missing required API key(s): "
                + ", ".join(missing)
                + ". Copy .env.example to .env and fill in values, "
                  "or set them as environment variables. "
                  "Get keys at https://www.omdbapi.com/apikey.aspx and "
                  "https://www.themoviedb.org/settings/api"
            )


def _load_env_file() -> None:
    if _load_dotenv is None:
        return
    if ENV_FILE.is_file():
        _load_dotenv(ENV_FILE, override=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings populated from env (and optional .env)."""
    _load_env_file()
    return Settings(
        omdb_api_key=os.environ.get("OMDB_API_KEY", "").strip(),
        tmdb_api_key=os.environ.get("TMDB_API_KEY", "").strip(),
    )


def reset_cache() -> None:
    """Clear cached Settings (useful in tests)."""
    get_settings.cache_clear()


if __name__ == "__main__":
    s = get_settings()
    print(f"OMDB_API_KEY: {'set' if s.omdb_api_key else 'MISSING'}")
    print(f"TMDB_API_KEY: {'set' if s.tmdb_api_key else 'MISSING'}")
    try:
        s.require_api_keys()
        print("OK - both keys present.")
    except ConfigError as e:
        print(f"ERROR: {e}")
        raise SystemExit(2)
