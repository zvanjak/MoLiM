"""
Spike (MoLiM-3ag): validate OMDb + TMDb hybrid against current
imdbAccess.fetchMovieData() data shape.

Reads OMDB_API_KEY and TMDB_API_KEY from environment (or .env).

Usage:
    python spike/spike_omdb_tmdb.py                       # runs against TestData/
    python spike/spike_omdb_tmdb.py "F1" 2025             # one-off lookup
    python spike/spike_omdb_tmdb.py --series "House of the Dragon"

Goal: prove OMDb (rating/votes) + TMDb (cast/crew/runtime/genres) together
yield every field IMDBMovieData / IMDBSeriesData currently expose.
Output is human-readable; missing fields are flagged with [GAP].
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


OMDB_KEY = os.environ.get("OMDB_API_KEY", "").strip()
TMDB_KEY = os.environ.get("TMDB_API_KEY", "").strip()

OMDB_URL = "http://www.omdbapi.com/"
TMDB_URL = "https://api.themoviedb.org/3"

# Fields IMDBMovieData currently exposes (from IMDBMovieData.py).
EXPECTED_MOVIE_FIELDS = [
    "imdb_name",
    "movieID",          # tt-id
    "year",
    "runtime",
    "rating",           # IMDb 0..10
    "votes",            # IMDb vote count
    "directors",
    "producers",
    "writers",
    "genres",
    "countries",
    "languages",
    "cover_url",
    "cast_leads",
    "cast_complete",
    "plot",
    "box_office",
    "top250rank",
    "releaseDate",
]


# ---------- HTTP helpers ----------------------------------------------------

def _get(url: str, params: dict[str, Any], timeout: float = 15.0) -> dict[str, Any]:
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


# ---------- OMDb ------------------------------------------------------------

def omdb_search(title: str, year: int | None = None) -> dict[str, Any] | None:
    if not OMDB_KEY:
        return None
    params = {"apikey": OMDB_KEY, "t": title, "type": "movie"}
    if year:
        params["y"] = str(year)
    data = _get(OMDB_URL, params)
    if data.get("Response") == "False":
        return None
    return data


def omdb_search_series(title: str) -> dict[str, Any] | None:
    if not OMDB_KEY:
        return None
    data = _get(OMDB_URL, {"apikey": OMDB_KEY, "t": title, "type": "series"})
    if data.get("Response") == "False":
        return None
    return data


def omdb_by_id(imdb_id: str) -> dict[str, Any] | None:
    if not OMDB_KEY:
        return None
    data = _get(OMDB_URL, {"apikey": OMDB_KEY, "i": imdb_id, "plot": "short"})
    if data.get("Response") == "False":
        return None
    return data


# ---------- TMDb ------------------------------------------------------------

def tmdb_find_by_imdb(imdb_id: str) -> dict[str, Any] | None:
    if not TMDB_KEY:
        return None
    return _get(
        f"{TMDB_URL}/find/{imdb_id}",
        {"api_key": TMDB_KEY, "external_source": "imdb_id"},
    )


def tmdb_movie(tmdb_id: int) -> dict[str, Any] | None:
    if not TMDB_KEY:
        return None
    return _get(
        f"{TMDB_URL}/movie/{tmdb_id}",
        {"api_key": TMDB_KEY, "append_to_response": "credits"},
    )


def tmdb_tv(tmdb_id: int) -> dict[str, Any] | None:
    if not TMDB_KEY:
        return None
    return _get(
        f"{TMDB_URL}/tv/{tmdb_id}",
        {"api_key": TMDB_KEY, "append_to_response": "credits,external_ids"},
    )


def tmdb_search_movie(title: str, year: int | None = None) -> dict[str, Any] | None:
    if not TMDB_KEY:
        return None
    params = {"api_key": TMDB_KEY, "query": title}
    if year:
        params["year"] = str(year)
    data = _get(f"{TMDB_URL}/search/movie", params)
    results = data.get("results") or []
    return results[0] if results else None


def tmdb_search_tv(title: str) -> dict[str, Any] | None:
    if not TMDB_KEY:
        return None
    data = _get(f"{TMDB_URL}/search/tv", {"api_key": TMDB_KEY, "query": title})
    results = data.get("results") or []
    return results[0] if results else None


# ---------- Hybrid merge ----------------------------------------------------

@dataclass
class HybridMovie:
    source_omdb: bool = False
    source_tmdb: bool = False
    fields: dict[str, Any] = field(default_factory=dict)
    gaps: list[str] = field(default_factory=list)

    def set(self, key: str, value: Any) -> None:
        if value not in (None, "", [], 0, "N/A"):
            self.fields[key] = value


def _names(items: list[dict[str, Any]], key: str = "name", limit: int | None = None) -> str:
    out = [i.get(key, "") for i in items if i.get(key)]
    if limit:
        out = out[:limit]
    return ", ".join(out)


def fetch_movie_hybrid(title: str, year: int | None) -> HybridMovie:
    """Mirror imdbAccess.fetchMovieData() return shape using OMDb + TMDb."""
    h = HybridMovie()

    # Step 1: OMDb gives us the IMDb id + ratings.
    omdb = omdb_search(title, year)
    imdb_id: str | None = None

    if omdb:
        h.source_omdb = True
        imdb_id = omdb.get("imdbID")
        h.set("imdb_name", omdb.get("Title"))
        h.set("movieID", imdb_id)
        h.set("year", _safe_int(omdb.get("Year")))
        h.set("rating", _safe_float(omdb.get("imdbRating")))
        h.set("votes", _safe_int((omdb.get("imdbVotes") or "").replace(",", "")))
        h.set("box_office", omdb.get("BoxOffice"))
        h.set("releaseDate", omdb.get("Released"))
        h.set("countries", omdb.get("Country"))
        h.set("languages", omdb.get("Language"))
        h.set("plot", omdb.get("Plot"))
        # OMDb runtime is "152 min"
        rt = omdb.get("Runtime", "")
        if rt and rt.endswith(" min"):
            h.set("runtime", _safe_int(rt.replace(" min", "")))
    else:
        h.gaps.append("omdb-miss-or-no-key")

    # Step 2: If we have an imdb_id, jump straight to TMDb. Otherwise search.
    tmdb_full: dict[str, Any] | None = None
    if imdb_id and TMDB_KEY:
        find = tmdb_find_by_imdb(imdb_id) or {}
        results = find.get("movie_results") or []
        if results:
            tmdb_full = tmdb_movie(results[0]["id"])
    if tmdb_full is None and TMDB_KEY:
        # fallback: title search
        s = tmdb_search_movie(title, year)
        if s:
            tmdb_full = tmdb_movie(s["id"])

    if tmdb_full:
        h.source_tmdb = True
        h.set("imdb_name", h.fields.get("imdb_name") or tmdb_full.get("title"))
        h.set("plot", h.fields.get("plot") or tmdb_full.get("overview"))
        h.set("runtime", h.fields.get("runtime") or tmdb_full.get("runtime"))
        h.set("releaseDate", h.fields.get("releaseDate") or tmdb_full.get("release_date"))
        # Year from TMDb release_date when OMDb is missing.
        if not h.fields.get("year") and tmdb_full.get("release_date"):
            h.set("year", _safe_int(tmdb_full["release_date"][:4]))
        h.set("genres", _names(tmdb_full.get("genres") or []))
        h.set("countries", h.fields.get("countries") or _names(tmdb_full.get("production_countries") or []))
        h.set("languages", h.fields.get("languages") or _names(tmdb_full.get("spoken_languages") or [], key="english_name"))

        poster = tmdb_full.get("poster_path")
        if poster:
            h.set("cover_url", f"https://image.tmdb.org/t/p/w500{poster}")

        credits = tmdb_full.get("credits") or {}
        cast = credits.get("cast") or []
        crew = credits.get("crew") or []
        h.set("cast_complete", _names(cast))
        h.set("cast_leads", _names(cast, limit=5))
        h.set("directors", _names([c for c in crew if c.get("job") == "Director"]))
        h.set("writers", _names([c for c in crew if c.get("department") == "Writing"]))
        h.set("producers", _names([c for c in crew if c.get("job") in ("Producer", "Executive Producer")], limit=6))

        if not imdb_id:
            ext_id = tmdb_full.get("imdb_id")
            if ext_id:
                h.set("movieID", ext_id)
    else:
        h.gaps.append("tmdb-miss-or-no-key")

    # Field-coverage report
    for field_name in EXPECTED_MOVIE_FIELDS:
        if field_name not in h.fields:
            h.gaps.append(f"missing:{field_name}")

    return h


def fetch_series_hybrid(title: str) -> HybridMovie:
    h = HybridMovie()

    omdb = omdb_search_series(title)
    imdb_id: str | None = None
    if omdb:
        h.source_omdb = True
        imdb_id = omdb.get("imdbID")
        h.set("imdb_name", omdb.get("Title"))
        h.set("movieID", imdb_id)
        h.set("year", omdb.get("Year"))  # series often "2022–"
        h.set("rating", _safe_float(omdb.get("imdbRating")))
        h.set("votes", _safe_int((omdb.get("imdbVotes") or "").replace(",", "")))
        h.set("plot", omdb.get("Plot"))
        h.set("countries", omdb.get("Country"))
        h.set("languages", omdb.get("Language"))
    else:
        h.gaps.append("omdb-miss-or-no-key")

    tmdb_full: dict[str, Any] | None = None
    if imdb_id and TMDB_KEY:
        find = tmdb_find_by_imdb(imdb_id) or {}
        results = find.get("tv_results") or []
        if results:
            tmdb_full = tmdb_tv(results[0]["id"])
    if tmdb_full is None and TMDB_KEY:
        s = tmdb_search_tv(title)
        if s:
            tmdb_full = tmdb_tv(s["id"])

    if tmdb_full:
        h.source_tmdb = True
        h.set("imdb_name", h.fields.get("imdb_name") or tmdb_full.get("name"))
        h.set("genres", _names(tmdb_full.get("genres") or []))
        h.set("releaseDate", tmdb_full.get("first_air_date"))
        h.set("countries", h.fields.get("countries") or _names(tmdb_full.get("production_countries") or []))
        h.set("languages", h.fields.get("languages") or _names(tmdb_full.get("spoken_languages") or [], key="english_name"))
        h.set("number_of_seasons", tmdb_full.get("number_of_seasons"))
        h.set("number_of_episodes", tmdb_full.get("number_of_episodes"))
        # episode runtime list
        ep_rt = tmdb_full.get("episode_run_time") or []
        if ep_rt:
            h.set("runtime", ep_rt[0])

        credits = tmdb_full.get("credits") or {}
        cast = credits.get("cast") or []
        crew = credits.get("crew") or []
        h.set("cast_leads", _names(cast, limit=10))
        h.set("cast_complete", _names(cast))
        # series creators come from `created_by`
        creators = tmdb_full.get("created_by") or []
        h.set("directors", _names(creators))  # closest analogue
        h.set("writers", _names([c for c in crew if c.get("department") == "Writing"]))
    else:
        h.gaps.append("tmdb-miss-or-no-key")

    return h


# ---------- utilities --------------------------------------------------------

def _safe_int(v: Any) -> int:
    try:
        return int(str(v).split("–")[0].split("-")[0])
    except (ValueError, TypeError):
        return 0


def _safe_float(v: Any) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


def _print_result(label: str, h: HybridMovie) -> None:
    print(f"\n=== {label} ===")
    print(f"  sources: omdb={h.source_omdb}  tmdb={h.source_tmdb}")
    for k, v in h.fields.items():
        sv = str(v)
        if len(sv) > 110:
            sv = sv[:107] + "..."
        print(f"  {k:20s} {sv}")
    if h.gaps:
        gaps = [g for g in h.gaps if g not in ("omdb-miss-or-no-key", "tmdb-miss-or-no-key")]
        misses = [g for g in h.gaps if g.startswith("missing:")]
        if misses:
            print("  [GAPS] " + ", ".join(g.replace("missing:", "") for g in misses))


# ---------- Folder-name parsing (matches FolderWithMovies behavior loosely)

def parse_folder_name(name: str) -> tuple[str, int | None]:
    """Strip ratings prefix and trailing release-info; return (title, year).
    Real parser lives in FolderWithMovies.py - this is a best-effort spike copy.
    """
    # strip leading underscore-rating prefix like "_8."
    s = name
    while s.startswith("_"):
        s = s[1:]
        # eat "8." style
        if len(s) >= 2 and s[0].isdigit() and s[1] == ".":
            s = s[2:]
    # title.year. or title.year (with optional release info after)
    import re

    m = re.match(r"^(.*?)[. ](\d{4})\b", s)
    if m:
        title = m.group(1).replace(".", " ").strip()
        return title, int(m.group(2))
    return s.replace(".", " ").strip(), None


# ---------- Main ------------------------------------------------------------

def _check_keys() -> bool:
    if not OMDB_KEY and not TMDB_KEY:
        print("ERROR: neither OMDB_API_KEY nor TMDB_API_KEY set.", file=sys.stderr)
        print("Copy .env.example to .env and fill in keys, or export env vars.", file=sys.stderr)
        return False
    if not OMDB_KEY:
        print("WARN: OMDB_API_KEY not set - rating/votes/box-office will be missing.")
    if not TMDB_KEY:
        print("WARN: TMDB_API_KEY not set - cast/crew/genres will be missing.")
    return True


def main() -> int:
    if not _check_keys():
        return 2

    args = sys.argv[1:]

    if len(args) >= 1 and args[0] == "--series":
        title = args[1] if len(args) > 1 else "House of the Dragon"
        h = fetch_series_hybrid(title)
        _print_result(f"series: {title}", h)
        return 0

    if len(args) >= 1:
        title = args[0]
        year = int(args[1]) if len(args) > 1 else None
        h = fetch_movie_hybrid(title, year)
        _print_result(f"{title} ({year})", h)
        return 0

    # Default: walk TestData/
    test_root = Path(__file__).resolve().parent.parent / "TestData"
    movies_dir = test_root / "Movies"
    series_dir = test_root / "Series"

    if movies_dir.is_dir():
        for folder in sorted(movies_dir.iterdir()):
            if not folder.is_dir():
                continue
            title, year = parse_folder_name(folder.name)
            try:
                h = fetch_movie_hybrid(title, year)
                _print_result(f"{folder.name} -> {title} ({year})", h)
            except requests.HTTPError as e:
                print(f"\n=== {folder.name} ===  HTTP ERROR: {e}")
            time.sleep(0.4)

    if series_dir.is_dir():
        for folder in sorted(series_dir.iterdir()):
            if not folder.is_dir():
                continue
            try:
                h = fetch_series_hybrid(folder.name)
                _print_result(f"series: {folder.name}", h)
            except requests.HTTPError as e:
                print(f"\n=== series: {folder.name} ===  HTTP ERROR: {e}")
            time.sleep(0.4)

    return 0


if __name__ == "__main__":
    sys.exit(main())
