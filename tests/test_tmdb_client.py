"""Unit tests for molim_data.tmdb_client (MoLiM-8yt)."""

from __future__ import annotations

import pytest

from molim_data.tmdb_client import (
    TMDbClient,
    TmdbAuthError,
    TmdbError,
    TmdbNotFound,
)
from tests.fixtures import (
    FakeResponse,
    FakeSession,
    tmdb_find_empty,
    tmdb_find_movie,
    tmdb_find_tv,
    tmdb_movie_matrix,
    tmdb_search_empty,
    tmdb_search_movie_results,
    tmdb_search_tv_results,
    tmdb_tv_breaking_bad,
)


def make_client(session: FakeSession, *, cast_leads: int = 5) -> TMDbClient:
    return TMDbClient(
        api_key="test-key",
        session=session,
        throttle_seconds=0,
        retries=0,
        cast_leads=cast_leads,
    )


class TestTmdbFind:
    def test_returns_movie_id(self):
        session = FakeSession().route("/find/tt0133093", FakeResponse(200, tmdb_find_movie()))
        result = make_client(session).find_by_imdb_id("tt0133093")
        assert result == {"movie_id": 603}

    def test_returns_tv_id(self):
        session = FakeSession().route("/find/tt0903747", FakeResponse(200, tmdb_find_tv()))
        result = make_client(session).find_by_imdb_id("tt0903747")
        assert result == {"tv_id": 1396}

    def test_empty_results_raises_not_found(self):
        session = FakeSession().route("/find/tt9999999", FakeResponse(200, tmdb_find_empty()))
        with pytest.raises(TmdbNotFound):
            make_client(session).find_by_imdb_id("tt9999999")

    def test_rejects_non_tt_id(self):
        with pytest.raises(ValueError):
            make_client(FakeSession()).find_by_imdb_id("603")


class TestTmdbGetMovie:
    def test_parses_full_movie(self):
        session = FakeSession().route("/movie/603", FakeResponse(200, tmdb_movie_matrix()))
        movie = make_client(session).get_movie(603)

        assert movie.tmdb_id == 603
        assert movie.imdb_id == "tt0133093"
        assert movie.title == "The Matrix"
        assert movie.year == 1999
        assert movie.runtime_min == 136
        assert movie.vote_average == 8.2
        assert movie.vote_count == 25000
        assert "Action" in movie.genres
        assert "Science Fiction" in movie.genres
        assert movie.poster_url and movie.poster_url.endswith(".jpg")
        assert movie.countries == ["United States of America"]
        assert movie.languages == ["English"]

    def test_credits_parsed(self):
        session = FakeSession().route("/movie/603", FakeResponse(200, tmdb_movie_matrix()))
        movie = make_client(session).get_movie(603)

        assert "Keanu Reeves" in movie.credits.cast_complete
        assert len(movie.credits.cast_leads) == 5
        assert movie.credits.cast_leads[0] == "Keanu Reeves"
        # Wachowskis appear twice in the crew (Director + Writer). Each list dedupes.
        assert movie.credits.directors == ["Lana Wachowski", "Lilly Wachowski"]
        assert movie.credits.writers == ["Lana Wachowski", "Lilly Wachowski"]
        assert "Joel Silver" in movie.credits.producers
        assert "Andrew Mason" in movie.credits.producers

    def test_cast_leads_respects_setting(self):
        session = FakeSession().route("/movie/603", FakeResponse(200, tmdb_movie_matrix()))
        movie = make_client(session, cast_leads=2).get_movie(603)
        assert len(movie.credits.cast_leads) == 2

    def test_appends_credits_in_query(self):
        session = FakeSession().route("/movie/603", FakeResponse(200, tmdb_movie_matrix()))
        make_client(session).get_movie(603)
        _url, params = session.calls[0]
        assert params.get("append_to_response") == "credits"
        assert params.get("api_key") == "test-key"


class TestTmdbGetTv:
    def test_parses_tv_with_external_imdb_id(self):
        session = FakeSession().route("/tv/1396", FakeResponse(200, tmdb_tv_breaking_bad()))
        tv = make_client(session).get_tv(1396)

        assert tv.tmdb_id == 1396
        assert tv.imdb_id == "tt0903747"
        assert tv.name == "Breaking Bad"
        assert tv.year == 2008
        assert tv.number_of_seasons == 5
        assert tv.episode_runtime == [49, 47]
        assert "Drama" in tv.genres
        assert tv.credits.cast_leads[0] == "Bryan Cranston"
        assert "Vince Gilligan" in tv.credits.writers


class TestTmdbSearch:
    def test_search_movie_then_get_movie(self):
        session = (
            FakeSession()
            .route("/search/movie", FakeResponse(200, tmdb_search_movie_results()))
            .route("/movie/603", FakeResponse(200, tmdb_movie_matrix()))
        )
        movie = make_client(session).search_movie("The Matrix", year=1999)
        assert movie.tmdb_id == 603

    def test_search_movie_empty_results_raises_not_found(self):
        session = FakeSession().route("/search/movie", FakeResponse(200, tmdb_search_empty()))
        with pytest.raises(TmdbNotFound):
            make_client(session).search_movie("Definitely Nothing", year=2099)

    def test_search_tv_then_get_tv(self):
        session = (
            FakeSession()
            .route("/search/tv", FakeResponse(200, tmdb_search_tv_results()))
            .route("/tv/1396", FakeResponse(200, tmdb_tv_breaking_bad()))
        )
        tv = make_client(session).search_tv("Breaking Bad")
        assert tv.tmdb_id == 1396

    def test_search_movie_empty_title_raises(self):
        with pytest.raises(ValueError):
            make_client(FakeSession()).search_movie("")

    def test_search_tv_empty_title_raises(self):
        with pytest.raises(ValueError):
            make_client(FakeSession()).search_tv("")


class TestTmdbErrors:
    def test_http_401_raises_auth(self):
        session = FakeSession().route("/movie/", FakeResponse(401, {}))
        with pytest.raises(TmdbAuthError):
            make_client(session).get_movie(603)

    def test_http_403_raises_auth(self):
        session = FakeSession().route("/movie/", FakeResponse(403, {}))
        with pytest.raises(TmdbAuthError):
            make_client(session).get_movie(603)

    def test_http_404_raises_not_found(self):
        session = FakeSession().route("/movie/", FakeResponse(404, {}))
        with pytest.raises(TmdbNotFound):
            make_client(session).get_movie(603)

    def test_http_500_raises_tmdb_error(self):
        session = FakeSession().route("/movie/", FakeResponse(500, {}))
        with pytest.raises(TmdbError):
            make_client(session).get_movie(603)
