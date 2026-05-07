"""Unit tests for molim_data.omdb_client (MoLiM-8yt)."""

from __future__ import annotations

import pytest

from molim_data.omdb_client import (
    OMDbClient,
    OmdbAuthError,
    OmdbError,
    OmdbNotFound,
)
from tests.fixtures import (
    FakeResponse,
    FakeSession,
    omdb_invalid_key,
    omdb_movie_matrix,
    omdb_movie_unrated_new_release,
    omdb_not_found,
    omdb_series_breaking_bad,
)


def make_client(session: FakeSession) -> OMDbClient:
    return OMDbClient(api_key="test-key", session=session, throttle_seconds=0, retries=0)


class TestOMDbClientSearchMovie:
    def test_returns_parsed_result(self):
        session = FakeSession().route("Matrix", FakeResponse(200, omdb_movie_matrix()))
        client = make_client(session)

        result = client.search_movie("The Matrix", year=1999)

        assert result.imdb_id == "tt0133093"
        assert result.title == "The Matrix"
        assert result.year == 1999
        assert result.type == "movie"
        assert result.imdb_rating == 8.7
        assert result.imdb_votes == 2_000_000
        assert result.runtime_min == 136
        assert result.box_office == "$172,076,928"
        assert result.released == "31 Mar 1999"

    def test_query_includes_title_year_and_apikey(self):
        session = FakeSession().route("Matrix", FakeResponse(200, omdb_movie_matrix()))
        make_client(session).search_movie("The Matrix", year=1999)

        _url, params = session.calls[0]
        assert params["t"] == "The Matrix"
        assert params["type"] == "movie"
        assert params["y"] == "1999"
        assert params["apikey"] == "test-key"

    def test_unrated_returns_none_rating(self):
        """OMDb 'N/A' must parse as None, not 0.0 (TMDb fallback relies on this)."""
        session = FakeSession().route("Brand", FakeResponse(200, omdb_movie_unrated_new_release()))
        result = make_client(session).search_movie("A Brand New Movie", year=2026)

        assert result.imdb_rating is None
        assert result.imdb_votes is None
        assert result.box_office is None

    def test_empty_title_raises(self):
        client = make_client(FakeSession())
        with pytest.raises(ValueError):
            client.search_movie("", year=1999)


class TestOMDbClientSearchSeries:
    def test_parses_ranged_year(self):
        """OMDb returns 'Year' as e.g. '2008-2013' for series; parser must take the start year."""
        session = FakeSession().route("Breaking", FakeResponse(200, omdb_series_breaking_bad()))
        result = make_client(session).search_series("Breaking Bad")

        assert result.year == 2008
        assert result.type == "series"
        assert result.imdb_rating == 9.5

    def test_query_uses_series_type(self):
        session = FakeSession().route("Breaking", FakeResponse(200, omdb_series_breaking_bad()))
        make_client(session).search_series("Breaking Bad")
        assert session.calls[0][1]["type"] == "series"


class TestOMDbClientGetByImdbId:
    def test_passes_imdb_id_as_i_param(self):
        session = FakeSession().route("tt0133093", FakeResponse(200, omdb_movie_matrix()))
        result = make_client(session).get_by_imdb_id("tt0133093")

        assert result.imdb_id == "tt0133093"
        assert session.calls[0][1]["i"] == "tt0133093"

    def test_rejects_non_tt_id(self):
        client = make_client(FakeSession())
        with pytest.raises(ValueError):
            client.get_by_imdb_id("0133093")


class TestOMDbClientErrors:
    def test_invalid_api_key_in_body_raises_auth_error(self):
        session = FakeSession().route("apikey", FakeResponse(200, omdb_invalid_key()))
        with pytest.raises(OmdbAuthError):
            make_client(session).search_movie("Anything")

    def test_http_401_raises_auth_error(self):
        session = FakeSession().route("apikey", FakeResponse(401, {"Error": "no"}))
        with pytest.raises(OmdbAuthError):
            make_client(session).search_movie("Anything")

    def test_not_found_raises_omdb_not_found(self):
        session = FakeSession().route("apikey", FakeResponse(200, omdb_not_found()))
        with pytest.raises(OmdbNotFound):
            make_client(session).search_movie("Definitely Not A Real Movie 12345")

    def test_http_500_raises_omdb_error(self):
        session = FakeSession().route("apikey", FakeResponse(500, {"Error": "boom"}))
        with pytest.raises(OmdbError):
            make_client(session).search_movie("Anything")

    def test_constructor_without_key_raises(self, monkeypatch):
        # OMDbClient calls get_settings() lazily when api_key is None.
        # Patch the symbol in the *omdb_client* module (it imported by name).
        import config
        from molim_data import omdb_client as omdb_mod
        monkeypatch.setattr(
            omdb_mod, "get_settings",
            lambda: config.Settings(omdb_api_key="", tmdb_api_key=""),
        )
        with pytest.raises(OmdbAuthError):
            OMDbClient(session=FakeSession())
