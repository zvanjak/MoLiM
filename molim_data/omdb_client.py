"""OMDb API client.

OMDb is the source of truth for IMDb rating + vote count + IMDb canonical
tt-ID. TMDb (see tmdb_client.py) supplies rich metadata. The two are
joined on the IMDb tt-ID.

Public surface:
    OMDbClient.get_by_imdb_id(tt_id)            -> OmdbResult
    OMDbClient.search_movie(title, year=None)   -> OmdbResult
    OMDbClient.search_series(title, year=None)  -> OmdbResult

Errors:
    OmdbAuthError   bad / missing API key (HTTP 401 or "Invalid API key!")
    OmdbNotFound    OMDb returned Response="False" with a "not found"-class
                    error
    OmdbError       any other failure (network, malformed JSON, 5xx after
                    retries)

Beads: MoLiM-6w5.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter

try:  # urllib3 v2 path; v1 fallback below
    from urllib3.util.retry import Retry
except ImportError:  # pragma: no cover - defensive
    from requests.packages.urllib3.util.retry import Retry  # type: ignore[no-redef]

from config import get_settings

log = logging.getLogger(__name__)


OMDB_URL = "http://www.omdbapi.com/"

DEFAULT_TIMEOUT = 15.0
DEFAULT_THROTTLE = 0.1  # seconds between calls; well under 1000/day budget
DEFAULT_RETRIES = 3


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #


class OmdbError(Exception):
    """Generic OMDb client failure."""


class OmdbAuthError(OmdbError):
    """OMDb rejected the API key."""


class OmdbNotFound(OmdbError):
    """OMDb has no record matching the query."""


# --------------------------------------------------------------------------- #
# Result dataclass
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class OmdbResult:
    """Subset of the OMDb payload that downstream code actually uses."""

    imdb_id: str                     # tt-ID, the cross-API join key
    title: str
    year: Optional[int]              # may be None for ranged series ("2022-")
    type: str                        # "movie" / "series" / "episode"
    imdb_rating: Optional[float]
    imdb_votes: Optional[int]
    runtime_min: Optional[int]
    box_office: Optional[str]        # left as raw "$152,300,000" string
    released: Optional[str]          # OMDb format "27 Jun 2025"
    countries: Optional[str]
    languages: Optional[str]
    plot: Optional[str]
    raw: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _safe_int(s: Any) -> Optional[int]:
    if s is None or s == "" or s == "N/A":
        return None
    try:
        return int(str(s).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _safe_float(s: Any) -> Optional[float]:
    if s is None or s == "" or s == "N/A":
        return None
    try:
        return float(str(s).strip())
    except (TypeError, ValueError):
        return None


def _opt_str(s: Any) -> Optional[str]:
    if s is None or s == "" or s == "N/A":
        return None
    return str(s)


def _parse_runtime(s: Any) -> Optional[int]:
    """OMDb 'Runtime' is e.g. '152 min'."""
    if not s or s == "N/A":
        return None
    s = str(s).strip()
    if s.lower().endswith(" min"):
        s = s[:-4]
    return _safe_int(s)


# --------------------------------------------------------------------------- #
# Client
# --------------------------------------------------------------------------- #


class OMDbClient:
    """Thin wrapper around the OMDb HTTP API.

    The session is created once per instance and reuses connections.
    Retries handle transient 5xx/429; logical errors (Response=False) are
    surfaced as exceptions.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        session: Optional[requests.Session] = None,
        timeout: float = DEFAULT_TIMEOUT,
        throttle_seconds: float = DEFAULT_THROTTLE,
        retries: int = DEFAULT_RETRIES,
    ) -> None:
        if api_key is None:
            api_key = get_settings().omdb_api_key
        if not api_key:
            raise OmdbAuthError(
                "OMDb API key is missing. Set OMDB_API_KEY in .env or "
                "pass api_key= explicitly."
            )
        self._api_key = api_key
        self._timeout = timeout
        self._throttle = throttle_seconds
        self._session = session if session is not None else self._build_session(retries)
        self._last_call_ts = 0.0

    # ----- public API ----------------------------------------------------- #

    def get_by_imdb_id(self, imdb_id: str, *, plot: str = "short") -> OmdbResult:
        if not imdb_id or not imdb_id.startswith("tt"):
            raise ValueError(f"Expected an IMDb tt-ID, got: {imdb_id!r}")
        return self._parse(self._call({"i": imdb_id, "plot": plot}))

    def search_movie(self, title: str, year: Optional[int] = None) -> OmdbResult:
        return self._search(title, year=year, type_="movie")

    def search_series(self, title: str, year: Optional[int] = None) -> OmdbResult:
        return self._search(title, year=year, type_="series")

    # ----- internals ------------------------------------------------------ #

    def _search(self, title: str, *, year: Optional[int], type_: str) -> OmdbResult:
        if not title:
            raise ValueError("title must be non-empty")
        params: dict[str, str] = {"t": title, "type": type_, "plot": "short"}
        if year:
            params["y"] = str(year)
        return self._parse(self._call(params))

    def _call(self, params: dict[str, str]) -> dict[str, Any]:
        params = {**params, "apikey": self._api_key}
        self._throttle_if_needed()
        try:
            resp = self._session.get(OMDB_URL, params=params, timeout=self._timeout)
        except requests.RequestException as exc:
            log.error("OMDb network error for %s: %s", _redact(params), exc)
            raise OmdbError(f"OMDb request failed: {exc}") from exc

        # urllib3 retries already covered 5xx + 429; anything else is final.
        if resp.status_code == 401:
            log.warning("OMDb returned 401 for %s", _redact(params))
            raise OmdbAuthError("OMDb rejected the API key (401).")
        if resp.status_code >= 400:
            log.error("OMDb HTTP %s for %s", resp.status_code, _redact(params))
            raise OmdbError(f"OMDb HTTP {resp.status_code}")

        try:
            data = resp.json()
        except ValueError as exc:
            log.error("OMDb returned non-JSON body: %.200s", resp.text)
            raise OmdbError("OMDb returned malformed JSON") from exc

        if isinstance(data, dict) and data.get("Response") == "False":
            err = (data.get("Error") or "").lower()
            if "invalid api key" in err or "no api key" in err:
                raise OmdbAuthError(data.get("Error") or "OMDb auth error")
            if "not found" in err or "incorrect imdb" in err:
                raise OmdbNotFound(data.get("Error") or "OMDb: not found")
            raise OmdbError(data.get("Error") or "OMDb error")

        return data

    @staticmethod
    def _parse(data: dict[str, Any]) -> OmdbResult:
        return OmdbResult(
            imdb_id=str(data.get("imdbID") or ""),
            title=str(data.get("Title") or ""),
            year=_safe_int((data.get("Year") or "").split("\u2013")[0].rstrip("-")),
            type=str(data.get("Type") or ""),
            imdb_rating=_safe_float(data.get("imdbRating")),
            imdb_votes=_safe_int(data.get("imdbVotes")),
            runtime_min=_parse_runtime(data.get("Runtime")),
            box_office=_opt_str(data.get("BoxOffice")),
            released=_opt_str(data.get("Released")),
            countries=_opt_str(data.get("Country")),
            languages=_opt_str(data.get("Language")),
            plot=_opt_str(data.get("Plot")),
            raw=data,
        )

    def _throttle_if_needed(self) -> None:
        if self._throttle <= 0:
            return
        elapsed = time.monotonic() - self._last_call_ts
        if elapsed < self._throttle:
            time.sleep(self._throttle - elapsed)
        self._last_call_ts = time.monotonic()

    @staticmethod
    def _build_session(retries: int) -> requests.Session:
        s = requests.Session()
        retry = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        s.headers.update({"User-Agent": "MoLiM/0.x (+https://github.com/zvanjak/MoLiM)"})
        return s


def _redact(params: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy of params with the api key masked, for logs."""
    return {k: ("***" if k == "apikey" else v) for k, v in params.items()}
