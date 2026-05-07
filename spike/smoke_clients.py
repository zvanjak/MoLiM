"""Quick end-to-end smoke against the real APIs (MoLiM-6w5/4rr).

Picks one movie (F1 2025) and one series (House of the Dragon), prints
key fields. Burns ~4 API calls. Run from repo root:

    .venv\\Scripts\\python.exe -m spike.smoke_clients
"""

from __future__ import annotations

import logging

from molim_data import OMDbClient, TMDbClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    omdb = OMDbClient()
    tmdb = TMDbClient()

    print("\n=== MOVIE: F1 (2025) via OMDb ===")
    f1 = omdb.search_movie("F1", year=2025)
    print(f"  imdb_id     : {f1.imdb_id}")
    print(f"  title/year  : {f1.title} ({f1.year})")
    print(f"  rating/votes: {f1.imdb_rating} / {f1.imdb_votes}")
    print(f"  box_office  : {f1.box_office}")
    print(f"  runtime     : {f1.runtime_min} min")
    print(f"  released    : {f1.released}")

    print("\n=== MOVIE: F1 via TMDb (joined by tt-ID) ===")
    found = tmdb.find_by_imdb_id(f1.imdb_id)
    print(f"  tmdb /find  : {found}")
    movie = tmdb.get_movie(found["movie_id"])
    print(f"  title       : {movie.title} ({movie.year})")
    print(f"  runtime     : {movie.runtime_min} min")
    print(f"  genres      : {', '.join(movie.genres)}")
    print(f"  directors   : {', '.join(movie.credits.directors)}")
    print(f"  writers     : {', '.join(movie.credits.writers)}")
    print(f"  producers   : {', '.join(movie.credits.producers)}")
    print(f"  cast leads  : {', '.join(movie.credits.cast_leads)}")
    print(f"  poster      : {movie.poster_url}")

    print("\n=== SERIES: House of the Dragon via OMDb ===")
    hotd = omdb.search_series("House of the Dragon")
    print(f"  imdb_id     : {hotd.imdb_id}")
    print(f"  title/year  : {hotd.title} ({hotd.year})")
    print(f"  rating/votes: {hotd.imdb_rating} / {hotd.imdb_votes}")

    print("\n=== SERIES: HotD via TMDb ===")
    found = tmdb.find_by_imdb_id(hotd.imdb_id)
    print(f"  tmdb /find  : {found}")
    tv = tmdb.get_tv(found["tv_id"])
    print(f"  name        : {tv.name} ({tv.year})")
    print(f"  seasons/eps : {tv.number_of_seasons} / {tv.number_of_episodes}")
    print(f"  ep runtime  : {tv.episode_runtime}")
    print(f"  genres      : {', '.join(tv.genres)}")
    print(f"  cast leads  : {', '.join(tv.credits.cast_leads)}")


if __name__ == "__main__":
    main()
