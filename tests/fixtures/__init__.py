"""Shared test fixtures: realistic OMDb / TMDb payloads + a FakeSession.

The FakeSession lets us drive OMDbClient / TMDbClient without touching the
network. It supports a per-URL-substring response map plus a fallback queue
for when tests need to script a sequence of calls (e.g. find -> get_movie).

Beads: MoLiM-8yt.
"""

from __future__ import annotations

import json
from collections import deque
from typing import Any, Optional


# --------------------------------------------------------------------------- #
# Fake HTTP plumbing
# --------------------------------------------------------------------------- #


class FakeResponse:
    def __init__(self, status_code: int, payload: Any = None, *, text: Optional[str] = None) -> None:
        self.status_code = status_code
        self._payload = payload
        if text is not None:
            self.text = text
        elif payload is None:
            self.text = ""
        else:
            try:
                self.text = json.dumps(payload)
            except (TypeError, ValueError):
                self.text = str(payload)

    def json(self) -> Any:
        if self._payload is None:
            raise ValueError("no JSON body")
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class FakeSession:
    """Minimal stand-in for requests.Session.

    Tests configure responses with `.route(url_or_param_substr, response)`
    or with `.queue(response, ...)`. Routes win over the queue. If neither
    matches, the call raises AssertionError so missing stubs are loud.
    """

    def __init__(self) -> None:
        self.headers: dict[str, str] = {}
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self._routes: list[tuple[str, FakeResponse]] = []
        self._queue: deque[FakeResponse] = deque()

    # configuration ---------------------------------------------------------

    def route(self, substr: str, response: FakeResponse) -> "FakeSession":
        self._routes.append((substr, response))
        return self

    def queue(self, *responses: FakeResponse) -> "FakeSession":
        self._queue.extend(responses)
        return self

    # session API used by the clients --------------------------------------

    def mount(self, *_a, **_kw) -> None:
        pass

    def get(self, url: str, params: Optional[dict[str, Any]] = None, timeout: Optional[float] = None) -> FakeResponse:
        params = params or {}
        self.calls.append((url, dict(params)))

        haystack = url + " " + " ".join(f"{k}={v}" for k, v in params.items())
        for substr, resp in self._routes:
            if substr in haystack:
                return resp

        if self._queue:
            return self._queue.popleft()

        raise AssertionError(f"FakeSession: no stubbed response for {url} params={params}")


# --------------------------------------------------------------------------- #
# OMDb payloads
# --------------------------------------------------------------------------- #


def omdb_movie_matrix() -> dict[str, Any]:
    return {
        "Title": "The Matrix",
        "Year": "1999",
        "Rated": "R",
        "Released": "31 Mar 1999",
        "Runtime": "136 min",
        "Genre": "Action, Sci-Fi",
        "Director": "Lana Wachowski, Lilly Wachowski",
        "Writer": "Lilly Wachowski, Lana Wachowski",
        "Actors": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss",
        "Plot": "A computer hacker learns from mysterious rebels about the true nature of his reality.",
        "Language": "English",
        "Country": "United States, Australia",
        "Poster": "https://example.com/matrix.jpg",
        "imdbRating": "8.7",
        "imdbVotes": "2,000,000",
        "imdbID": "tt0133093",
        "Type": "movie",
        "BoxOffice": "$172,076,928",
        "Response": "True",
    }


def omdb_movie_unrated_new_release() -> dict[str, Any]:
    """OMDb shape for a fresh release: imdbRating='N/A'. Triggers TMDb fallback."""
    return {
        "Title": "A Brand New Movie",
        "Year": "2026",
        "Rated": "N/A",
        "Released": "01 May 2026",
        "Runtime": "120 min",
        "Genre": "Drama",
        "Director": "Some Director",
        "Writer": "Some Writer",
        "Actors": "Some Actor",
        "Plot": "N/A",
        "Language": "English",
        "Country": "United States",
        "Poster": "N/A",
        "imdbRating": "N/A",
        "imdbVotes": "N/A",
        "imdbID": "tt99999991",
        "Type": "movie",
        "BoxOffice": "N/A",
        "Response": "True",
    }


def omdb_series_breaking_bad() -> dict[str, Any]:
    return {
        "Title": "Breaking Bad",
        "Year": "2008\u20132013",
        "Rated": "TV-MA",
        "Released": "20 Jan 2008",
        "Runtime": "49 min",
        "Genre": "Crime, Drama, Thriller",
        "Director": "N/A",
        "Writer": "Vince Gilligan",
        "Actors": "Bryan Cranston, Aaron Paul, Anna Gunn",
        "Plot": "A high school chemistry teacher diagnosed with terminal lung cancer turns to manufacturing meth.",
        "Language": "English, Spanish",
        "Country": "United States",
        "Poster": "https://example.com/bb.jpg",
        "imdbRating": "9.5",
        "imdbVotes": "2,200,000",
        "imdbID": "tt0903747",
        "Type": "series",
        "totalSeasons": "5",
        "Response": "True",
    }


def omdb_not_found() -> dict[str, Any]:
    return {"Response": "False", "Error": "Movie not found!"}


def omdb_invalid_key() -> dict[str, Any]:
    return {"Response": "False", "Error": "Invalid API key!"}


# --------------------------------------------------------------------------- #
# TMDb payloads
# --------------------------------------------------------------------------- #


def tmdb_find_movie() -> dict[str, Any]:
    return {
        "movie_results": [{"id": 603, "title": "The Matrix"}],
        "tv_results": [],
        "person_results": [],
    }


def tmdb_find_tv() -> dict[str, Any]:
    return {
        "movie_results": [],
        "tv_results": [{"id": 1396, "name": "Breaking Bad"}],
        "person_results": [],
    }


def tmdb_find_empty() -> dict[str, Any]:
    return {"movie_results": [], "tv_results": [], "person_results": []}


def tmdb_movie_matrix() -> dict[str, Any]:
    return {
        "id": 603,
        "imdb_id": "tt0133093",
        "title": "The Matrix",
        "original_title": "The Matrix",
        "overview": "Set in the 22nd century, The Matrix tells the story of a computer hacker.",
        "runtime": 136,
        "release_date": "1999-03-30",
        "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Science Fiction"}],
        "production_countries": [{"iso_3166_1": "US", "name": "United States of America"}],
        "spoken_languages": [{"iso_639_1": "en", "english_name": "English", "name": "English"}],
        "poster_path": "/p96dm7sCMn4VYAStA6siNz30G93.jpg",
        "vote_average": 8.2,
        "vote_count": 25000,
        "credits": {
            "cast": [
                {"name": "Keanu Reeves", "character": "Neo", "order": 0},
                {"name": "Laurence Fishburne", "character": "Morpheus", "order": 1},
                {"name": "Carrie-Anne Moss", "character": "Trinity", "order": 2},
                {"name": "Hugo Weaving", "character": "Agent Smith", "order": 3},
                {"name": "Joe Pantoliano", "character": "Cypher", "order": 4},
                {"name": "Marcus Chong", "character": "Tank", "order": 5},
            ],
            "crew": [
                {"name": "Lana Wachowski", "job": "Director", "department": "Directing"},
                {"name": "Lilly Wachowski", "job": "Director", "department": "Directing"},
                {"name": "Lana Wachowski", "job": "Writer", "department": "Writing"},
                {"name": "Lilly Wachowski", "job": "Writer", "department": "Writing"},
                {"name": "Joel Silver", "job": "Producer", "department": "Production"},
                {"name": "Andrew Mason", "job": "Executive Producer", "department": "Production"},
            ],
        },
    }


def tmdb_movie_unrated() -> dict[str, Any]:
    """TMDb shape with an actual vote_average that should override OMDb's N/A."""
    return {
        "id": 999991,
        "imdb_id": "tt99999991",
        "title": "A Brand New Movie",
        "original_title": "A Brand New Movie",
        "overview": "Plot from TMDb.",
        "runtime": 120,
        "release_date": "2026-05-01",
        "genres": [{"id": 18, "name": "Drama"}],
        "production_countries": [{"iso_3166_1": "US", "name": "United States of America"}],
        "spoken_languages": [{"iso_639_1": "en", "english_name": "English", "name": "English"}],
        "poster_path": "/abc.jpg",
        "vote_average": 7.2,
        "vote_count": 142,
        "credits": {"cast": [], "crew": []},
    }


def tmdb_tv_breaking_bad() -> dict[str, Any]:
    return {
        "id": 1396,
        "name": "Breaking Bad",
        "original_name": "Breaking Bad",
        "overview": "When Walter White, a chemistry teacher, is diagnosed with terminal cancer...",
        "first_air_date": "2008-01-20",
        "last_air_date": "2013-09-29",
        "number_of_seasons": 5,
        "number_of_episodes": 62,
        "episode_run_time": [49, 47],
        "genres": [{"id": 18, "name": "Drama"}, {"id": 80, "name": "Crime"}],
        "production_countries": [{"iso_3166_1": "US", "name": "United States of America"}],
        "spoken_languages": [{"iso_639_1": "en", "english_name": "English", "name": "English"}],
        "poster_path": "/bb.jpg",
        "vote_average": 8.9,
        "vote_count": 14000,
        "external_ids": {"imdb_id": "tt0903747"},
        "credits": {
            "cast": [
                {"name": "Bryan Cranston", "character": "Walter White", "order": 0},
                {"name": "Aaron Paul", "character": "Jesse Pinkman", "order": 1},
                {"name": "Anna Gunn", "character": "Skyler White", "order": 2},
            ],
            "crew": [
                {"name": "Vince Gilligan", "job": "Writer", "department": "Writing"},
                {"name": "Vince Gilligan", "job": "Executive Producer", "department": "Production"},
            ],
        },
    }


def tmdb_search_movie_results() -> dict[str, Any]:
    return {"page": 1, "results": [{"id": 603, "title": "The Matrix"}], "total_results": 1}


def tmdb_search_tv_results() -> dict[str, Any]:
    return {"page": 1, "results": [{"id": 1396, "name": "Breaking Bad"}], "total_results": 1}


def tmdb_search_empty() -> dict[str, Any]:
    return {"page": 1, "results": [], "total_results": 0}
