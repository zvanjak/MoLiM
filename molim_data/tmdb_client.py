"""TMDb API client.

Companion to OMDbClient. TMDb provides cast, crew, runtime, genres,
posters, and (for series) season/episode structure. The IMDb tt-ID
acts as the join key via the /find endpoint.

Public surface:
    TMDbClient.find_by_imdb_id(tt_id) -> {"movie_id": int} | {"tv_id": int}
    TMDbClient.get_movie(tmdb_id)     -> TmdbMovie
    TMDbClient.get_tv(tmdb_id)        -> TmdbTv
    TMDbClient.get_tv_season(tv_id, season_number) -> dict (raw)
    TMDbClient.search_movie(title, year=None)      -> TmdbMovie
    TMDbClient.search_tv(title)                    -> TmdbTv

Errors:
    TmdbAuthError   401 / 403
    TmdbNotFound    404 or empty find/search result
    TmdbError       any other failure

Auth: v3 API key passed as 'api_key' query param. (We chose v3 because the
key the user already has is a v3 key.)

Beads: MoLiM-4rr.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

import requests
from requests.adapters import HTTPAdapter

try:
    from urllib3.util.retry import Retry
except ImportError:  # pragma: no cover
    from requests.packages.urllib3.util.retry import Retry  # type: ignore[no-redef]

from config import get_settings

log = logging.getLogger(__name__)


TMDB_URL = "https://api.themoviedb.org/3"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"

DEFAULT_TIMEOUT = 15.0
DEFAULT_THROTTLE = 0.05  # TMDb is ~50 req/sec; we don't need this much
DEFAULT_RETRIES = 3
DEFAULT_CAST_LEADS = 5


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #


class TmdbError(Exception):
    """Generic TMDb client failure."""


class TmdbAuthError(TmdbError):
    """TMDb rejected the API key."""


class TmdbNotFound(TmdbError):
    """TMDb has no record matching the query."""


# --------------------------------------------------------------------------- #
# Result dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class TmdbCredits:
    cast_complete: list[str]                       # all cast member names, in order
    cast_leads: list[str]                          # first N (default 5)
    cast_with_characters: list[tuple[str, str]]    # (name, character)
    directors: list[str]
    writers: list[str]                             # deduped, ordered
    producers: list[str]                           # Producer + Executive Producer


@dataclass(frozen=True)
class TmdbMovie:
    tmdb_id: int
    imdb_id: Optional[str]
    title: str
    original_title: Optional[str]
    overview: Optional[str]
    runtime_min: Optional[int]
    release_date: Optional[str]                    # ISO "YYYY-MM-DD"
    year: Optional[int]
    genres: list[str]
    countries: list[str]
    languages: list[str]
    poster_url: Optional[str]
    credits: TmdbCredits
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TmdbTv:
    tmdb_id: int
    imdb_id: Optional[str]
    name: str
    original_name: Optional[str]
    overview: Optional[str]
    first_air_date: Optional[str]
    last_air_date: Optional[str]
    year: Optional[int]
    number_of_seasons: Optional[int]
    number_of_episodes: Optional[int]
    episode_runtime: list[int]
    genres: list[str]
    countries: list[str]
    languages: list[str]
    poster_url: Optional[str]
    credits: TmdbCredits
    raw: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _safe_int(s: Any) -> Optional[int]:
    if s in (None, "", "N/A"):
        return None
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def _names(items: Iterable[dict[str, Any]], key: str = "name") -> list[str]:
    return [str(i.get(key)) for i in items if i.get(key)]


def _dedupe(seq: Iterable[str]) -> list[str]:
    """Order-preserving dedupe."""
    seen: set[str] = set()
    out: list[str] = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _year_from(date_str: Optional[str]) -> Optional[int]:
    if not date_str:
        return None
    return _safe_int(date_str[:4])


def _poster_url(poster_path: Optional[str]) -> Optional[str]:
    if not poster_path:
        return None
    return f"{TMDB_IMG_BASE}{poster_path}"


# --------------------------------------------------------------------------- #
# Client
# --------------------------------------------------------------------------- #


class TMDbClient:
    """HTTP client for TMDb v3."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        session: Optional[requests.Session] = None,
        timeout: float = DEFAULT_TIMEOUT,
        throttle_seconds: float = DEFAULT_THROTTLE,
        retries: int = DEFAULT_RETRIES,
        cast_leads: int = DEFAULT_CAST_LEADS,
    ) -> None:
        if api_key is None:
            api_key = get_settings().tmdb_api_key
        if not api_key:
            raise TmdbAuthError(
                "TMDb API key is missing. Set TMDB_API_KEY in .env or "
                "pass api_key= explicitly."
            )
        self._api_key = api_key
        self._timeout = timeout
        self._throttle = throttle_seconds
        self._session = session if session is not None else self._build_session(retries)
        self._last_call_ts = 0.0
        self._cast_leads = max(1, cast_leads)

    # ----- public API ----------------------------------------------------- #

    def find_by_imdb_id(self, imdb_id: str) -> dict[str, int]:
        """Return {"movie_id": int} or {"tv_id": int} for the first match.

        Raises TmdbNotFound if neither flavour matches.
        """
        if not imdb_id or not imdb_id.startswith("tt"):
            raise ValueError(f"Expected an IMDb tt-ID, got: {imdb_id!r}")
        data = self._get(f"/find/{imdb_id}", {"external_source": "imdb_id"})
        movies = data.get("movie_results") or []
        tvs = data.get("tv_results") or []
        if movies:
            return {"movie_id": int(movies[0]["id"])}
        if tvs:
            return {"tv_id": int(tvs[0]["id"])}
        raise TmdbNotFound(f"TMDb /find returned no results for {imdb_id}")

    def get_movie(self, tmdb_id: int) -> TmdbMovie:
        data = self._get(f"/movie/{tmdb_id}", {"append_to_response": "credits"})
        return self._parse_movie(data)

    def get_tv(self, tmdb_id: int) -> TmdbTv:
        data = self._get(
            f"/tv/{tmdb_id}",
            {"append_to_response": "credits,external_ids"},
        )
        return self._parse_tv(data)

    def get_tv_season(self, tmdb_id: int, season_number: int) -> dict[str, Any]:
        return self._get(f"/tv/{tmdb_id}/season/{season_number}", {})

    def search_movie(self, title: str, year: Optional[int] = None) -> TmdbMovie:
        if not title:
            raise ValueError("title must be non-empty")
        params: dict[str, str] = {"query": title}
        if year:
            params["year"] = str(year)
        data = self._get("/search/movie", params)
        results = data.get("results") or []
        if not results:
            raise TmdbNotFound(f"TMDb /search/movie: no results for {title!r}")
        return self.get_movie(int(results[0]["id"]))

    def search_tv(self, title: str) -> TmdbTv:
        if not title:
            raise ValueError("title must be non-empty")
        data = self._get("/search/tv", {"query": title})
        results = data.get("results") or []
        if not results:
            raise TmdbNotFound(f"TMDb /search/tv: no results for {title!r}")
        return self.get_tv(int(results[0]["id"]))

    # ----- internals ------------------------------------------------------ #

    def _get(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        url = f"{TMDB_URL}{path}"
        full = {**params, "api_key": self._api_key}
        self._throttle_if_needed()
        try:
            resp = self._session.get(url, params=full, timeout=self._timeout)
        except requests.RequestException as exc:
            log.error("TMDb network error for %s: %s", path, exc)
            raise TmdbError(f"TMDb request failed: {exc}") from exc

        if resp.status_code in (401, 403):
            log.warning("TMDb auth failure (%s) for %s", resp.status_code, path)
            raise TmdbAuthError(f"TMDb rejected the API key ({resp.status_code}).")
        if resp.status_code == 404:
            raise TmdbNotFound(f"TMDb 404 for {path}")
        if resp.status_code >= 400:
            log.error("TMDb HTTP %s for %s", resp.status_code, path)
            raise TmdbError(f"TMDb HTTP {resp.status_code}")

        try:
            return resp.json()
        except ValueError as exc:
            log.error("TMDb returned non-JSON body for %s: %.200s", path, resp.text)
            raise TmdbError("TMDb returned malformed JSON") from exc

    def _parse_movie(self, data: dict[str, Any]) -> TmdbMovie:
        credits = self._parse_credits(data.get("credits") or {})
        release_date = data.get("release_date") or None
        return TmdbMovie(
            tmdb_id=int(data.get("id") or 0),
            imdb_id=(data.get("imdb_id") or None),
            title=str(data.get("title") or ""),
            original_title=(data.get("original_title") or None),
            overview=(data.get("overview") or None),
            runtime_min=_safe_int(data.get("runtime")),
            release_date=release_date,
            year=_year_from(release_date),
            genres=_names(data.get("genres") or []),
            countries=_names(data.get("production_countries") or []),
            languages=_names(data.get("spoken_languages") or [], key="english_name")
                       or _names(data.get("spoken_languages") or []),
            poster_url=_poster_url(data.get("poster_path")),
            credits=credits,
            raw=data,
        )

    def _parse_tv(self, data: dict[str, Any]) -> TmdbTv:
        credits = self._parse_credits(data.get("credits") or {})
        first_air = data.get("first_air_date") or None
        ext = data.get("external_ids") or {}
        return TmdbTv(
            tmdb_id=int(data.get("id") or 0),
            imdb_id=(ext.get("imdb_id") or None),
            name=str(data.get("name") or ""),
            original_name=(data.get("original_name") or None),
            overview=(data.get("overview") or None),
            first_air_date=first_air,
            last_air_date=(data.get("last_air_date") or None),
            year=_year_from(first_air),
            number_of_seasons=_safe_int(data.get("number_of_seasons")),
            number_of_episodes=_safe_int(data.get("number_of_episodes")),
            episode_runtime=[
                int(n) for n in (data.get("episode_run_time") or []) if isinstance(n, (int, float))
            ],
            genres=_names(data.get("genres") or []),
            countries=_names(data.get("production_countries") or [])
                       or _names(data.get("origin_country") or [], key="iso_3166_1")
                       or list(data.get("origin_country") or []),
            languages=_names(data.get("spoken_languages") or [], key="english_name")
                       or _names(data.get("spoken_languages") or []),
            poster_url=_poster_url(data.get("poster_path")),
            credits=credits,
            raw=data,
        )

    def _parse_credits(self, credits: dict[str, Any]) -> TmdbCredits:
        cast = credits.get("cast") or []
        crew = credits.get("crew") or []

        cast_names = _names(cast)
        cast_with_chars = [
            (str(c.get("name") or ""), str(c.get("character") or ""))
            for c in cast
            if c.get("name")
        ]

        directors = _dedupe(c.get("name", "") for c in crew if c.get("job") == "Director")
        writers = _dedupe(
            c.get("name", "")
            for c in crew
            if c.get("department") == "Writing" and c.get("name")
        )
        producers = _dedupe(
            c.get("name", "")
            for c in crew
            if c.get("job") in ("Producer", "Executive Producer") and c.get("name")
        )

        return TmdbCredits(
            cast_complete=cast_names,
            cast_leads=cast_names[: self._cast_leads],
            cast_with_characters=cast_with_chars,
            directors=directors,
            writers=writers,
            producers=producers,
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
