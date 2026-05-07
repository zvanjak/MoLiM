"""MovieDataService: hybrid OMDb + TMDb orchestration.

Replaces the cinemagoer-based fetchers in imdbAccess.py. Returns
IMDBMovieData / IMDBSeriesData instances populated with the same
field shape so existing call sites only need their import swapped.

Failure contract (preserves cinemagoer behaviour):
    On any unrecoverable failure, the returned object's `.name` is
    set to "" - this is the sentinel callers already check.

Caching:
    JSON-file cache under ./cache/ keyed by IMDb tt-ID.
    TTL configurable (default 30 days). When the API call succeeds
    we write the merged dict; on next lookup within TTL we restore
    from disk and skip both API calls.

Field merge precedence:
    - rating, votes, box_office, releaseDate (raw OMDb format),
      countries, languages          : OMDb wins (canonical IMDb)
    - cast, crew, runtime, genres,
      poster                        : TMDb wins (richer metadata)
    - plot                          : OMDb if present, else TMDb overview
    - imdb_name / title             : OMDb if present, else TMDb

Beads: MoLiM-bjo.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

import IMDBMovieData
import IMDBSeriesData

from molim_data.omdb_client import (
    OMDbClient,
    OmdbAuthError,
    OmdbError,
    OmdbNotFound,
    OmdbResult,
)
from molim_data.tmdb_client import (
    TMDbClient,
    TmdbAuthError,
    TmdbError,
    TmdbMovie,
    TmdbNotFound,
    TmdbTv,
)

log = logging.getLogger(__name__)


DEFAULT_CACHE_DIR = Path("cache")
DEFAULT_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days
CACHE_VERSION = 1


# --------------------------------------------------------------------------- #
# Service
# --------------------------------------------------------------------------- #


class MovieDataService:
    """Orchestrates OMDb (rating/votes) + TMDb (metadata) lookups.

    Construct once per app run. Keeps an OMDbClient + TMDbClient with
    persistent HTTP sessions. Cache is on-disk JSON.
    """

    def __init__(
        self,
        *,
        omdb: Optional[OMDbClient] = None,
        tmdb: Optional[TMDbClient] = None,
        cache_dir: Path | str = DEFAULT_CACHE_DIR,
        cache_ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        self._omdb = omdb if omdb is not None else OMDbClient()
        self._tmdb = tmdb if tmdb is not None else TMDbClient()
        self._cache_dir = Path(cache_dir)
        self._cache_ttl = cache_ttl_seconds

    # ----- public API ----------------------------------------------------- #

    def get_movie(self, title: str, year: Optional[int]) -> IMDBMovieData.IMDBMovieData:
        """Fetch a movie by (title, year). Returns IMDBMovieData; on
        failure `.name == ""`."""
        out = IMDBMovieData.IMDBMovieData(title)
        try:
            omdb = self._omdb.search_movie(title, year=year)
        except OmdbAuthError as exc:
            log.error("OMDb auth failure: %s", exc)
            out.name = ""
            return out
        except OmdbNotFound:
            log.warning("OMDb: no movie match for %r (%s)", title, year)
            return self._fallback_movie_via_tmdb(title, year, out)
        except OmdbError as exc:
            log.warning("OMDb error for %r (%s): %s", title, year, exc)
            return self._fallback_movie_via_tmdb(title, year, out)

        return self._merge_movie(title, omdb, out)

    def get_movie_by_imdb_id(self, imdb_id: str, *, name: Optional[str] = None) -> IMDBMovieData.IMDBMovieData:
        out = IMDBMovieData.IMDBMovieData(name or imdb_id)
        try:
            omdb = self._omdb.get_by_imdb_id(imdb_id)
        except OmdbError as exc:
            log.error("OMDb get_by_imdb_id %s failed: %s", imdb_id, exc)
            out.name = ""
            return out
        return self._merge_movie(out.name, omdb, out)

    def get_series(self, title: str) -> IMDBSeriesData.IMDBSeriesData:
        out = IMDBSeriesData.IMDBSeriesData(title)
        try:
            omdb = self._omdb.search_series(title)
        except OmdbAuthError as exc:
            log.error("OMDb auth failure: %s", exc)
            out.name = ""
            return out
        except OmdbNotFound:
            log.warning("OMDb: no series match for %r", title)
            return self._fallback_series_via_tmdb(title, out)
        except OmdbError as exc:
            log.warning("OMDb error for series %r: %s", title, exc)
            return self._fallback_series_via_tmdb(title, out)

        return self._merge_series(title, omdb, out)

    def get_series_by_imdb_id(self, imdb_id: str, *, name: Optional[str] = None) -> IMDBSeriesData.IMDBSeriesData:
        out = IMDBSeriesData.IMDBSeriesData(name or imdb_id)
        try:
            omdb = self._omdb.get_by_imdb_id(imdb_id)
        except OmdbError as exc:
            log.error("OMDb get_by_imdb_id %s failed: %s", imdb_id, exc)
            out.name = ""
            return out
        return self._merge_series(out.name, omdb, out)

    # ----- merge: movie --------------------------------------------------- #

    def _merge_movie(
        self,
        name: str,
        omdb: OmdbResult,
        out: IMDBMovieData.IMDBMovieData,
    ) -> IMDBMovieData.IMDBMovieData:
        cached = self._cache_load(omdb.imdb_id)
        if cached is not None:
            return _movie_from_cache(name, cached)

        # Fill the OMDb-canonical fields first.
        out.movieID = omdb.imdb_id or 0
        out.imdb_name = omdb.title or ""
        out.year = omdb.year or 0
        out.rating = omdb.imdb_rating if omdb.imdb_rating is not None else 0.0
        out.votes = omdb.imdb_votes or 0
        out.box_office = omdb.box_office or ""
        out.releaseDate = omdb.released or ""
        out.countries = omdb.countries or ""
        out.languages = omdb.languages or ""
        out.runtime = omdb.runtime_min or 0
        if omdb.plot:
            out.plot = omdb.plot

        # Now enrich with TMDb.
        tmdb_movie = self._lookup_tmdb_movie(omdb.imdb_id, fallback_title=name, fallback_year=omdb.year)
        if tmdb_movie is not None:
            self._apply_tmdb_movie(out, tmdb_movie)

        self._cache_store(omdb.imdb_id, _movie_to_cache(out, omdb, tmdb_movie))
        return out

    def _fallback_movie_via_tmdb(
        self,
        title: str,
        year: Optional[int],
        out: IMDBMovieData.IMDBMovieData,
    ) -> IMDBMovieData.IMDBMovieData:
        try:
            tmdb_movie = self._tmdb.search_movie(title, year=year)
        except (TmdbAuthError, TmdbNotFound, TmdbError) as exc:
            log.warning("TMDb fallback failed for %r (%s): %s", title, year, exc)
            out.name = ""
            return out
        self._apply_tmdb_movie(out, tmdb_movie)
        if tmdb_movie.imdb_id:
            out.movieID = tmdb_movie.imdb_id
        return out

    def _lookup_tmdb_movie(
        self,
        imdb_id: str,
        *,
        fallback_title: str,
        fallback_year: Optional[int],
    ) -> Optional[TmdbMovie]:
        try:
            if imdb_id:
                found = self._tmdb.find_by_imdb_id(imdb_id)
                if "movie_id" in found:
                    return self._tmdb.get_movie(found["movie_id"])
        except TmdbNotFound:
            pass
        except (TmdbAuthError, TmdbError) as exc:
            log.warning("TMDb find failed for %s: %s", imdb_id, exc)
            return None

        try:
            return self._tmdb.search_movie(fallback_title, year=fallback_year)
        except (TmdbAuthError, TmdbNotFound, TmdbError) as exc:
            log.warning("TMDb search_movie fallback failed for %r: %s", fallback_title, exc)
            return None

    def _apply_tmdb_movie(
        self,
        out: IMDBMovieData.IMDBMovieData,
        m: TmdbMovie,
    ) -> None:
        if not out.imdb_name:
            out.imdb_name = m.title
        if not out.year and m.year:
            out.year = m.year
        if not out.runtime and m.runtime_min:
            out.runtime = m.runtime_min
        if not out.releaseDate and m.release_date:
            out.releaseDate = m.release_date
        if not out.plot and m.overview:
            out.plot = m.overview
        if not out.countries and m.countries:
            out.countries = ", ".join(m.countries)
        if not out.languages and m.languages:
            out.languages = ", ".join(m.languages)
        if m.poster_url:
            out.cover_url = m.poster_url
        if m.genres:
            out.genres = ", ".join(m.genres) + ", "
        if m.credits.directors:
            out.directors = ", ".join(m.credits.directors)
        if m.credits.writers:
            out.writers = ", ".join(m.credits.writers)
        if m.credits.producers:
            out.producers = ", ".join(m.credits.producers)
        if m.credits.cast_complete:
            out.cast_complete = ", ".join(m.credits.cast_complete) + ", "
        if m.credits.cast_leads:
            out.cast_leads = ", ".join(m.credits.cast_leads) + ", "

    # ----- merge: series -------------------------------------------------- #

    def _merge_series(
        self,
        name: str,
        omdb: OmdbResult,
        out: IMDBSeriesData.IMDBSeriesData,
    ) -> IMDBSeriesData.IMDBSeriesData:
        cached = self._cache_load(omdb.imdb_id)
        if cached is not None:
            return _series_from_cache(name, cached)

        out.movieID = omdb.imdb_id or 0
        out.imdb_name = omdb.title or ""
        out.year = omdb.year or 0
        out.rating = omdb.imdb_rating if omdb.imdb_rating is not None else 0.0
        out.votes = omdb.imdb_votes or 0
        out.releaseDate = omdb.released or ""
        out.countries = omdb.countries or ""
        out.languages = omdb.languages or ""
        out.runtime = omdb.runtime_min or 0
        if omdb.plot:
            out.plot = omdb.plot

        tmdb_tv = self._lookup_tmdb_tv(omdb.imdb_id, fallback_title=name)
        if tmdb_tv is not None:
            self._apply_tmdb_tv(out, tmdb_tv)

        self._cache_store(omdb.imdb_id, _series_to_cache(out, omdb, tmdb_tv))
        return out

    def _fallback_series_via_tmdb(
        self,
        title: str,
        out: IMDBSeriesData.IMDBSeriesData,
    ) -> IMDBSeriesData.IMDBSeriesData:
        try:
            tv = self._tmdb.search_tv(title)
        except (TmdbAuthError, TmdbNotFound, TmdbError) as exc:
            log.warning("TMDb tv fallback failed for %r: %s", title, exc)
            out.name = ""
            return out
        self._apply_tmdb_tv(out, tv)
        if tv.imdb_id:
            out.movieID = tv.imdb_id
        return out

    def _lookup_tmdb_tv(
        self,
        imdb_id: str,
        *,
        fallback_title: str,
    ) -> Optional[TmdbTv]:
        try:
            if imdb_id:
                found = self._tmdb.find_by_imdb_id(imdb_id)
                if "tv_id" in found:
                    return self._tmdb.get_tv(found["tv_id"])
        except TmdbNotFound:
            pass
        except (TmdbAuthError, TmdbError) as exc:
            log.warning("TMDb find tv failed for %s: %s", imdb_id, exc)
            return None

        try:
            return self._tmdb.search_tv(fallback_title)
        except (TmdbAuthError, TmdbNotFound, TmdbError) as exc:
            log.warning("TMDb search_tv fallback failed for %r: %s", fallback_title, exc)
            return None

    def _apply_tmdb_tv(
        self,
        out: IMDBSeriesData.IMDBSeriesData,
        tv: TmdbTv,
    ) -> None:
        if not out.imdb_name:
            out.imdb_name = tv.name
        if not out.year and tv.year:
            out.year = tv.year
        if not out.releaseDate and tv.first_air_date:
            out.releaseDate = tv.first_air_date
        if not out.plot and tv.overview:
            out.plot = tv.overview
        if not out.countries and tv.countries:
            out.countries = ", ".join(tv.countries)
        if not out.languages and tv.languages:
            out.languages = ", ".join(tv.languages)
        if tv.poster_url:
            out.cover_url = tv.poster_url
        if tv.genres:
            out.genres = ", ".join(tv.genres) + ", "
        if tv.number_of_seasons:
            out.num_seasons = tv.number_of_seasons
        if not out.runtime and tv.episode_runtime:
            out.runtime = tv.episode_runtime[0]
        if tv.credits.writers:
            out.writers = ", ".join(tv.credits.writers)
        if tv.credits.cast_complete:
            out.cast_complete = ", ".join(tv.credits.cast_complete) + ", "
        if tv.credits.cast_leads:
            out.cast_leads = ", ".join(tv.credits.cast_leads) + ", "
        # Note: seasons_list is left empty here; episode-level data is a
        # separate concern (will be wired in alongside MoLiM-cqh if needed).

    # ----- cache ---------------------------------------------------------- #

    def _cache_path(self, imdb_id: str) -> Optional[Path]:
        if not imdb_id or not imdb_id.startswith("tt"):
            return None
        return self._cache_dir / f"{imdb_id}.json"

    def _cache_load(self, imdb_id: str) -> Optional[dict[str, Any]]:
        path = self._cache_path(imdb_id)
        if path is None or not path.exists():
            return None
        try:
            age = time.time() - path.stat().st_mtime
            if age > self._cache_ttl:
                log.debug("Cache stale for %s (%.0fs old)", imdb_id, age)
                return None
            with path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            if payload.get("_v") != CACHE_VERSION:
                return None
            return payload
        except (OSError, ValueError) as exc:
            log.warning("Cache read failed for %s: %s", imdb_id, exc)
            return None

    def _cache_store(self, imdb_id: str, payload: dict[str, Any]) -> None:
        path = self._cache_path(imdb_id)
        if path is None:
            return
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            payload = {"_v": CACHE_VERSION, **payload}
            with path.open("w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2, default=_json_default)
        except OSError as exc:
            log.warning("Cache write failed for %s: %s", imdb_id, exc)


# --------------------------------------------------------------------------- #
# Cache (de)serialization
# --------------------------------------------------------------------------- #

# We snapshot the *result fields*, not the API payloads, so changes to the
# clients don't invalidate caches as long as the mapping stays stable.

_MOVIE_FIELDS = (
    "imdb_name", "movieID", "year", "runtime", "rating", "votes",
    "directors", "producers", "writers", "genres", "countries", "languages",
    "cover_url", "cast_leads", "cast_complete", "plot", "box_office",
    "top250rank", "releaseDate",
)

_SERIES_FIELDS = (
    "imdb_name", "movieID", "year", "num_seasons", "runtime", "rating", "votes",
    "writers", "genres", "countries", "languages", "cover_url",
    "cast_leads", "cast_complete", "plot", "releaseDate",
)


def _movie_to_cache(out: IMDBMovieData.IMDBMovieData, omdb: OmdbResult, tmdb: Optional[TmdbMovie]) -> dict[str, Any]:
    return {"kind": "movie", "fields": {k: getattr(out, k) for k in _MOVIE_FIELDS}}


def _movie_from_cache(name: str, payload: dict[str, Any]) -> IMDBMovieData.IMDBMovieData:
    out = IMDBMovieData.IMDBMovieData(name)
    for k, v in (payload.get("fields") or {}).items():
        if hasattr(out, k):
            setattr(out, k, v)
    return out


def _series_to_cache(out: IMDBSeriesData.IMDBSeriesData, omdb: OmdbResult, tmdb: Optional[TmdbTv]) -> dict[str, Any]:
    return {"kind": "series", "fields": {k: getattr(out, k) for k in _SERIES_FIELDS}}


def _series_from_cache(name: str, payload: dict[str, Any]) -> IMDBSeriesData.IMDBSeriesData:
    out = IMDBSeriesData.IMDBSeriesData(name)
    for k, v in (payload.get("fields") or {}).items():
        if hasattr(out, k):
            setattr(out, k, v)
    return out


def _json_default(obj: Any) -> Any:
    # Fallback for unexpected objects in the merged record.
    try:
        return asdict(obj)
    except TypeError:
        return str(obj)
