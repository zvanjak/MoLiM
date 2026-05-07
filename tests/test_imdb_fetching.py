"""Tests for imdbAccess.py - the compatibility shim over MovieDataService.

The real network is never touched; we monkeypatch imdbAccess._service with
a MagicMock and verify the shim's contracts:

  * empty/whitespace title -> SKIPPED, returns IMDBMovieData with name=""
  * fetchMovieData / fetchSeriesData delegate to the service
  * fetchMovieDataByMovieID / fetchSeriesDataByMovieID normalize the ID
    (cinemagoer-style bare digits -> 'tt' + zero-padded 7-digit form)
  * a malformed movieID short-circuits to name=""

Beads: MoLiM-8yt.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import imdbAccess
from IMDBMovieData import IMDBMovieData
from IMDBSeriesData import IMDBSeriesData


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture
def fake_service(monkeypatch):
    """Replace imdbAccess._service with a MagicMock and yield it."""
    svc = MagicMock()
    monkeypatch.setattr(imdbAccess, "_service", svc)
    monkeypatch.setattr(imdbAccess, "_get_service", lambda: svc)
    return svc


def _movie(name="The Matrix", **kw):
    md = IMDBMovieData(name)
    md.movieID = kw.get("movieID", "tt0133093")
    md.rating = kw.get("rating", 8.7)
    md.votes = kw.get("votes", 2_000_000)
    md.year = kw.get("year", 1999)
    md.runtime = kw.get("runtime", 136)
    md.directors = kw.get("directors", "Lana Wachowski, Lilly Wachowski")
    md.producers = kw.get("producers", "Joel Silver")
    md.writers = kw.get("writers", "Lana Wachowski")
    md.genres = kw.get("genres", "Action, Sci-Fi, ")
    md.cast_leads = kw.get("cast_leads", "Keanu Reeves, ")
    return md


def _series(name="Breaking Bad", **kw):
    sd = IMDBSeriesData(name)
    sd.movieID = kw.get("movieID", "tt0903747")
    sd.rating = kw.get("rating", 9.5)
    sd.year = kw.get("year", 2008)
    sd.num_seasons = kw.get("num_seasons", 5)
    sd.genres = kw.get("genres", "Crime, Drama, ")
    sd.cast_leads = kw.get("cast_leads", "Bryan Cranston, ")
    return sd


# --------------------------------------------------------------------------- #
# fetchMovieData
# --------------------------------------------------------------------------- #


class TestFetchMovieData:
    def test_delegates_to_service(self, fake_service):
        fake_service.get_movie.return_value = _movie()
        out = imdbAccess.fetchMovieData("The Matrix", 1999)

        fake_service.get_movie.assert_called_once_with("The Matrix", 1999)
        assert out.movieID == "tt0133093"
        assert out.rating == 8.7

    def test_year_zero_passed_as_none(self, fake_service):
        fake_service.get_movie.return_value = _movie()
        imdbAccess.fetchMovieData("The Matrix", 0)
        fake_service.get_movie.assert_called_once_with("The Matrix", None)

    def test_empty_title_skips_without_calling_service(self, fake_service):
        out = imdbAccess.fetchMovieData("", 2020)

        assert out.name == ""
        fake_service.get_movie.assert_not_called()

    def test_whitespace_title_skips(self, fake_service):
        out = imdbAccess.fetchMovieData("   ", 2020)

        assert out.name == ""
        fake_service.get_movie.assert_not_called()

    def test_strips_trailing_whitespace_from_title(self, fake_service):
        fake_service.get_movie.return_value = _movie()
        imdbAccess.fetchMovieData("The Matrix   ", 1999)
        fake_service.get_movie.assert_called_once_with("The Matrix", 1999)


class TestFetchMovieDataByMovieID:
    @pytest.mark.parametrize(
        "given,expected",
        [
            ("tt0133093", "tt0133093"),
            ("0133093", "tt0133093"),
            ("133093", "tt0133093"),
            ("tt133093", "tt0133093"),
            ("TT0133093", "tt0133093"),
        ],
    )
    def test_normalizes_id(self, fake_service, given, expected):
        fake_service.get_movie_by_imdb_id.return_value = _movie()
        imdbAccess.fetchMovieDataByMovieID("The Matrix", given)
        fake_service.get_movie_by_imdb_id.assert_called_once_with(expected, name="The Matrix")

    @pytest.mark.parametrize("bad", [None, "", "0", "abc"])
    def test_invalid_id_returns_empty(self, fake_service, bad):
        out = imdbAccess.fetchMovieDataByMovieID("X", bad)

        assert out.name == ""
        fake_service.get_movie_by_imdb_id.assert_not_called()


# --------------------------------------------------------------------------- #
# fetchSeriesData / by ID
# --------------------------------------------------------------------------- #


class TestFetchSeriesData:
    def test_delegates_to_service(self, fake_service):
        fake_service.get_series.return_value = _series()
        out = imdbAccess.fetchSeriesData("Breaking Bad")

        fake_service.get_series.assert_called_once_with("Breaking Bad")
        assert out.movieID == "tt0903747"
        assert out.rating == 9.5


class TestFetchSeriesDataByMovieID:
    def test_normalizes_id_and_passes_name(self, fake_service):
        fake_service.get_series_by_imdb_id.return_value = _series()
        imdbAccess.fetchSeriesDataByMovieID("Breaking Bad", "0903747")
        fake_service.get_series_by_imdb_id.assert_called_once_with("tt0903747", name="Breaking Bad")

    def test_invalid_id_returns_empty(self, fake_service):
        out = imdbAccess.fetchSeriesDataByMovieID("X", "garbage")

        assert out.name == ""
        fake_service.get_series_by_imdb_id.assert_not_called()


# --------------------------------------------------------------------------- #
# Failure-shape contract: service-side empty must propagate name=""
# --------------------------------------------------------------------------- #


class TestServiceFailurePropagates:
    def test_movie_lookup_failure_propagates_empty_name(self, fake_service):
        empty = IMDBMovieData("anything")
        empty.name = ""
        fake_service.get_movie.return_value = empty

        out = imdbAccess.fetchMovieData("Anything", 2020)
        assert out.name == ""

    def test_series_lookup_failure_propagates_empty_name(self, fake_service):
        empty = IMDBSeriesData("anything")
        empty.name = ""
        fake_service.get_series.return_value = empty

        out = imdbAccess.fetchSeriesData("Anything")
        assert out.name == ""
