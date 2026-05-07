"""imdbAccess: thin compatibility shim over MovieDataService.

Historically this module wrapped cinemagoer. The cinemagoer scraper
became unreliable (rating/votes drift, missing fields), so as of the
MoLiM-02x migration it now delegates to MovieDataService - a hybrid
OMDb (rating/votes/box_office) + TMDb (cast/crew/genres/poster)
orchestrator with on-disk caching.

Public function signatures are preserved verbatim so the existing
call sites in processing.py / FolderWithMovies.py / etc. don't change.

Failure contract is preserved: on any unrecoverable error the returned
object's `.name` is set to "" - callers already check for this.

Beads: MoLiM-cqh, MoLiM-bjo.
"""

from __future__ import annotations

import logging
from typing import Optional

import IMDBMovieData
import IMDBSeriesData

from molim_data import MovieDataService

log = logging.getLogger(__name__)


# Module-level singleton. Created lazily so imports stay cheap and
# tests can monkeypatch _service or _get_service() before the first
# call.
_service: Optional[MovieDataService] = None


def _get_service() -> MovieDataService:
    global _service
    if _service is None:
        _service = MovieDataService()
    return _service


def _normalize_imdb_id(movie_id) -> str:
    """Accepts cinemagoer-style bare digits ('0133093'), the legacy
    integer 0 placeholder, or full 'tt'-prefixed IDs ('tt0133093').
    Returns a canonical 'ttNNNNNNN' string. Raises ValueError on garbage.
    """
    if movie_id is None:
        raise ValueError("movieID is None")
    s = str(movie_id).strip()
    if not s or s == "0":
        raise ValueError(f"invalid movieID: {movie_id!r}")
    if s.lower().startswith("tt"):
        return "tt" + s[2:].lstrip("0").zfill(7)
    if s.isdigit():
        return "tt" + s.lstrip("0").zfill(7)
    raise ValueError(f"unrecognized movieID format: {movie_id!r}")


def _print_movie_summary(md: IMDBMovieData.IMDBMovieData) -> None:
    if md.name == "":
        print("   ----   LOOKUP FAILED   ----")
        return
    print("IMDB rating:  {0}".format(md.rating))
    print("Num. votes:   {0}".format(md.votes))
    if md.box_office:
        print("Box office:   {0}".format(md.box_office))
    if md.releaseDate:
        print("Release date: {0}".format(md.releaseDate))
    print("Year:         {0}".format(md.year))
    print("Runtime:      {0} min".format(md.runtime))
    print("Directors:    " + md.directors)
    prods = md.producers
    if len(prods) > 120:
        prods = prods[:120] + "..."
    print("Producers:    " + prods)
    print("Writers:      " + md.writers)
    print("Genres:       " + md.genres)
    print("Cast:         " + md.cast_leads)
    print()


def _print_series_summary(sd: IMDBSeriesData.IMDBSeriesData) -> None:
    if sd.name == "":
        print("   ----   LOOKUP FAILED   ----")
        return
    print("IMDB rating:  {0}".format(sd.rating))
    print("Num. votes:   {0}".format(sd.votes))
    print("Year:         {0}".format(sd.year))
    print("Seasons:      {0}".format(getattr(sd, "num_seasons", 0)))
    print("Genres:       " + sd.genres)
    print("Cast:         " + sd.cast_leads)
    print()


# --------------------------------------------------------------------------- #
# Public API (preserved from the cinemagoer-era module)
# --------------------------------------------------------------------------- #


def fetchMovieData(searchMovieName: str, releaseYear) -> IMDBMovieData.IMDBMovieData:
    """Search OMDb (with TMDb fallback) for a movie by title + year.

    `releaseYear` may be an int or 0/None when the year is unknown.
    """
    name = (searchMovieName or "").rstrip()
    year = int(releaseYear) if releaseYear else None
    print(f"Fetching movie: {name!r} ({year})")
    if not name:
        print("   ----   SKIPPED: could not parse a title from folder name")
        out = IMDBMovieData.IMDBMovieData("")
        out.name = ""
        return out
    md = _get_service().get_movie(name, year)
    _print_movie_summary(md)
    return md


def fetchMovieDataByMovieID(name: str, movieID) -> IMDBMovieData.IMDBMovieData:
    """Fetch a movie directly by its IMDb ID. Accepts cinemagoer-style
    digits or 'tt'-prefixed IDs."""
    try:
        imdb_id = _normalize_imdb_id(movieID)
    except ValueError as exc:
        log.error("fetchMovieDataByMovieID: %s", exc)
        out = IMDBMovieData.IMDBMovieData(name)
        out.name = ""
        return out
    print(f"Fetching movie by ID: {imdb_id} ({name!r})")
    md = _get_service().get_movie_by_imdb_id(imdb_id, name=name)
    _print_movie_summary(md)
    return md


def fetchSeriesData(searchSeriesName: str) -> IMDBSeriesData.IMDBSeriesData:
    name = (searchSeriesName or "").rstrip()
    print(f"Fetching series: {name!r}")
    sd = _get_service().get_series(name)
    _print_series_summary(sd)
    return sd


def fetchSeriesDataByMovieID(name: str, movieID) -> IMDBSeriesData.IMDBSeriesData:
    try:
        imdb_id = _normalize_imdb_id(movieID)
    except ValueError as exc:
        log.error("fetchSeriesDataByMovieID: %s", exc)
        out = IMDBSeriesData.IMDBSeriesData(name)
        out.name = ""
        return out
    print(f"Fetching series by ID: {imdb_id} ({name!r})")
    sd = _get_service().get_series_by_imdb_id(imdb_id, name=name)
    _print_series_summary(sd)
    return sd
