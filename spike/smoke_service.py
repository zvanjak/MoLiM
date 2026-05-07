"""Smoke test for MovieDataService (MoLiM-bjo).

Runs against the real OMDb + TMDb APIs once, verifies cache hit on
the second call (no API traffic, fast). Uses a tmp cache dir so it
doesn't pollute the real one.

    .venv\\Scripts\\python.exe -m spike.smoke_service
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import time
from pathlib import Path

from molim_data import MovieDataService

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def _print_movie(label: str, m) -> None:
    print(f"\n--- {label} ---")
    print(f"  name        : {m.name}")
    print(f"  imdb_name   : {m.imdb_name}")
    print(f"  movieID     : {m.movieID}")
    print(f"  year        : {m.year}")
    print(f"  runtime     : {m.runtime} min")
    print(f"  rating/votes: {m.rating} / {m.votes}")
    print(f"  box_office  : {m.box_office}")
    print(f"  releaseDate : {m.releaseDate}")
    print(f"  directors   : {m.directors}")
    print(f"  writers     : {m.writers}")
    print(f"  producers   : {m.producers[:120]}...")
    print(f"  genres      : {m.genres}")
    print(f"  countries   : {m.countries}")
    print(f"  languages   : {m.languages}")
    print(f"  cast_leads  : {m.cast_leads}")
    print(f"  cover_url   : {m.cover_url}")
    print(f"  plot[:80]   : {(m.plot or '')[:80]}")


def _print_series(label: str, s) -> None:
    print(f"\n--- {label} ---")
    print(f"  name        : {s.name}")
    print(f"  imdb_name   : {s.imdb_name}")
    print(f"  movieID     : {s.movieID}")
    print(f"  year        : {s.year}")
    print(f"  num_seasons : {s.num_seasons}")
    print(f"  rating/votes: {s.rating} / {s.votes}")
    print(f"  genres      : {s.genres}")
    print(f"  cast_leads  : {s.cast_leads}")


def main() -> None:
    cache_dir = Path(tempfile.mkdtemp(prefix="molim-cache-"))
    print(f"Using temp cache dir: {cache_dir}")
    try:
        svc = MovieDataService(cache_dir=cache_dir)

        t0 = time.perf_counter()
        f1 = svc.get_movie("F1", 2025)
        t_first = time.perf_counter() - t0
        _print_movie(f"F1 (2025) - first lookup ({t_first:.2f}s)", f1)

        t0 = time.perf_counter()
        f1_cached = svc.get_movie("F1", 2025)
        t_second = time.perf_counter() - t0
        print(f"\nCache hit timing: {t_second*1000:.1f}ms (was {t_first*1000:.0f}ms cold)")
        assert f1_cached.movieID == f1.movieID
        assert f1_cached.rating == f1.rating
        assert (cache_dir / f"{f1.movieID}.json").exists(), "cache file not written"

        sinners = svc.get_movie("Sinners", 2025)
        _print_movie("Sinners (2025)", sinners)

        accountant = svc.get_movie("The Accountant 2", 2025)
        _print_movie("The Accountant 2 (2025)", accountant)

        hotd = svc.get_series("House of the Dragon")
        _print_series("House of the Dragon", hotd)

        # Failure path
        bogus = svc.get_movie("zzzzz-this-will-not-exist-2099", 2099)
        print(f"\nBogus lookup -> name={bogus.name!r} (should be empty string)")
        assert bogus.name == "", "expected empty name on full failure"

        print("\nOK - all assertions passed.")
    finally:
        shutil.rmtree(cache_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
