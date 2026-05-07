"""Unit tests for molim_data.movie_data_service (MoLiM-8yt).

These exercise the merge / fallback / caching logic by injecting fake
OMDb + TMDb clients (built as MagicMocks). The OmdbResult / TmdbMovie /
TmdbTv values are produced via the real client parsers, so wire-format
changes are caught here too.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from molim_data.movie_data_service import MovieDataService
from molim_data.omdb_client import OMDbClient, OmdbAuthError, OmdbError, OmdbNotFound
from molim_data.tmdb_client import TMDbClient, TmdbNotFound
from tests.fixtures import (
    omdb_movie_matrix,
    omdb_movie_unrated_new_release,
    omdb_series_breaking_bad,
    tmdb_find_movie,
    tmdb_find_tv,
    tmdb_movie_matrix,
    tmdb_movie_unrated,
    tmdb_season_payload,
    tmdb_tv_breaking_bad,
    tmdb_tv_two_seasons,
)


# --------------------------------------------------------------------------- #
# Helpers - build real result objects from fixtures via the real parsers
# --------------------------------------------------------------------------- #


def _omdb_result_from(payload):
    return OMDbClient._parse(payload)


def _build_tmdb_clientside_movie(payload):
    """Run the real TMDb parser on a fixture dict to get a TmdbMovie."""
    client = TMDbClient(api_key="x", session=MagicMock(), throttle_seconds=0, retries=0)
    return client._parse_movie(payload)


def _build_tmdb_clientside_tv(payload):
    client = TMDbClient(api_key="x", session=MagicMock(), throttle_seconds=0, retries=0)
    return client._parse_tv(payload)


def _make_service(*, omdb=None, tmdb=None, tmp_cache):
    return MovieDataService(
        omdb=omdb,
        tmdb=tmdb,
        cache_dir=tmp_cache,
        cache_ttl_seconds=3600,
    )


@pytest.fixture
def cache_dir(tmp_path):
    return tmp_path / "cache"


# --------------------------------------------------------------------------- #
# get_movie
# --------------------------------------------------------------------------- #


class TestGetMovieHappyPath:
    def test_merges_omdb_and_tmdb(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_movie.return_value = _omdb_result_from(omdb_movie_matrix())

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.find_by_imdb_id.return_value = {"movie_id": 603}
        tmdb.get_movie.return_value = _build_tmdb_clientside_movie(tmdb_movie_matrix())

        svc = _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir)
        md = svc.get_movie("The Matrix", 1999)

        # OMDb-canonical
        assert md.movieID == "tt0133093"
        assert md.rating == 8.7
        assert md.votes == 2_000_000
        assert md.box_office == "$172,076,928"
        assert md.year == 1999

        # TMDb-canonical (rich metadata)
        assert "Keanu Reeves" in md.cast_complete
        assert "Lana Wachowski" in md.directors
        assert "Lilly Wachowski" in md.directors
        assert "Action" in md.genres
        assert md.cover_url and md.cover_url.endswith(".jpg")

    def test_uses_find_then_get_when_imdb_id_present(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_movie.return_value = _omdb_result_from(omdb_movie_matrix())

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.find_by_imdb_id.return_value = {"movie_id": 603}
        tmdb.get_movie.return_value = _build_tmdb_clientside_movie(tmdb_movie_matrix())

        _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir).get_movie("The Matrix", 1999)

        tmdb.find_by_imdb_id.assert_called_once_with("tt0133093")
        tmdb.get_movie.assert_called_once_with(603)
        tmdb.search_movie.assert_not_called()

    def test_falls_back_to_tmdb_search_when_find_returns_not_found(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_movie.return_value = _omdb_result_from(omdb_movie_matrix())

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.find_by_imdb_id.side_effect = TmdbNotFound("nope")
        tmdb.search_movie.return_value = _build_tmdb_clientside_movie(tmdb_movie_matrix())

        _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir).get_movie("The Matrix", 1999)

        tmdb.search_movie.assert_called_once()


class TestGetMovieRatingFallback:
    def test_uses_tmdb_vote_average_when_omdb_rating_missing(self, cache_dir):
        """The MoLiM-5ml fallback: unrated new releases get TMDb's vote_average."""
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_movie.return_value = _omdb_result_from(omdb_movie_unrated_new_release())

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.find_by_imdb_id.return_value = {"movie_id": 999991}
        tmdb.get_movie.return_value = _build_tmdb_clientside_movie(tmdb_movie_unrated())

        svc = _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir)
        md = svc.get_movie("A Brand New Movie", 2026)

        assert md.rating == 7.2
        assert md.votes == 142


class TestGetMovieFailureModes:
    def test_omdb_auth_error_returns_empty_name(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_movie.side_effect = OmdbAuthError("bad key")

        svc = _make_service(omdb=omdb, tmdb=MagicMock(spec=TMDbClient), tmp_cache=cache_dir)
        md = svc.get_movie("Anything", 2020)

        assert md.name == ""

    def test_omdb_not_found_falls_back_to_tmdb_search(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_movie.side_effect = OmdbNotFound("nope")

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.search_movie.return_value = _build_tmdb_clientside_movie(tmdb_movie_matrix())

        svc = _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir)
        md = svc.get_movie("The Matrix", 1999)

        assert md.name != ""
        assert md.movieID == "tt0133093"
        # OMDb had nothing - rating must come from TMDb
        assert md.rating == 8.2
        tmdb.search_movie.assert_called_once_with("The Matrix", year=1999)

    def test_omdb_error_with_tmdb_also_failing_returns_empty(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_movie.side_effect = OmdbError("oops")

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.search_movie.side_effect = TmdbNotFound("nope")

        svc = _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir)
        md = svc.get_movie("Whatever", 2020)

        assert md.name == ""


class TestGetMovieByImdbId:
    def test_short_circuits_via_get_by_imdb_id(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.get_by_imdb_id.return_value = _omdb_result_from(omdb_movie_matrix())

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.find_by_imdb_id.return_value = {"movie_id": 603}
        tmdb.get_movie.return_value = _build_tmdb_clientside_movie(tmdb_movie_matrix())

        svc = _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir)
        md = svc.get_movie_by_imdb_id("tt0133093", name="The Matrix")

        omdb.get_by_imdb_id.assert_called_once_with("tt0133093")
        omdb.search_movie.assert_not_called()
        assert md.movieID == "tt0133093"


# --------------------------------------------------------------------------- #
# get_series
# --------------------------------------------------------------------------- #


class TestGetSeriesHappyPath:
    def test_merges_omdb_and_tmdb_series(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_series.return_value = _omdb_result_from(omdb_series_breaking_bad())

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.find_by_imdb_id.return_value = {"tv_id": 1396}
        tmdb.get_tv.return_value = _build_tmdb_clientside_tv(tmdb_tv_breaking_bad())
        # Skip per-season fetches in this base test (covered by TestSeasonWiring)
        tmdb.get_tv_season.side_effect = TmdbNotFound("skip")

        svc = _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir)
        sd = svc.get_series("Breaking Bad")

        assert sd.movieID == "tt0903747"
        assert sd.rating == 9.5
        assert sd.year == 2008
        assert sd.num_seasons == 5
        assert "Bryan Cranston" in sd.cast_complete
        assert "Vince Gilligan" in sd.writers


class TestGetSeriesFallbackPath:
    def test_omdb_not_found_falls_back_to_tmdb_search_tv(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_series.side_effect = OmdbNotFound("nope")

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.search_tv.return_value = _build_tmdb_clientside_tv(tmdb_tv_breaking_bad())
        tmdb.get_tv_season.side_effect = TmdbNotFound("skip")

        svc = _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir)
        sd = svc.get_series("Breaking Bad")

        assert sd.name != ""
        assert sd.movieID == "tt0903747"
        tmdb.search_tv.assert_called_once_with("Breaking Bad")


# --------------------------------------------------------------------------- #
# Cache
# --------------------------------------------------------------------------- #


class TestCache:
    def test_second_call_reuses_cache_and_skips_tmdb(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_movie.return_value = _omdb_result_from(omdb_movie_matrix())

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.find_by_imdb_id.return_value = {"movie_id": 603}
        tmdb.get_movie.return_value = _build_tmdb_clientside_movie(tmdb_movie_matrix())

        svc = _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir)

        first = svc.get_movie("The Matrix", 1999)
        # Second call: cache file exists, so TMDb shouldn't be re-hit.
        tmdb.reset_mock()
        second = svc.get_movie("The Matrix", 1999)

        assert second.movieID == first.movieID
        assert second.rating == first.rating
        assert "Keanu Reeves" in second.cast_complete
        tmdb.find_by_imdb_id.assert_not_called()
        tmdb.get_movie.assert_not_called()

    def test_cache_file_written_with_version(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_movie.return_value = _omdb_result_from(omdb_movie_matrix())
        tmdb = MagicMock(spec=TMDbClient)
        tmdb.find_by_imdb_id.return_value = {"movie_id": 603}
        tmdb.get_movie.return_value = _build_tmdb_clientside_movie(tmdb_movie_matrix())

        _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir).get_movie("The Matrix", 1999)

        cache_file = cache_dir / "tt0133093.json"
        assert cache_file.exists()
        import json
        payload = json.loads(cache_file.read_text(encoding="utf-8"))
        assert payload["_v"] == 2  # CACHE_VERSION
        assert payload["kind"] == "movie"
        assert payload["fields"]["movieID"] == "tt0133093"


# --------------------------------------------------------------------------- #
# Episode/Season wiring (MoLiM-ywz)
# --------------------------------------------------------------------------- #


def _build_tmdb_clientside_season(payload):
    client = TMDbClient(api_key="x", session=MagicMock(), throttle_seconds=0, retries=0)
    return client._parse_tv_season(payload)


class TestSeasonWiring:
    def _build_service(self, cache_dir):
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_series.return_value = _omdb_result_from(omdb_series_breaking_bad())

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.find_by_imdb_id.return_value = {"tv_id": 4242}
        tmdb.get_tv.return_value = _build_tmdb_clientside_tv(tmdb_tv_two_seasons())
        tmdb.get_tv_season.side_effect = lambda tv_id, n: _build_tmdb_clientside_season(
            tmdb_season_payload(n, episodes=2)
        )
        return omdb, tmdb, _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir)

    def test_seasons_and_episodes_populated(self, cache_dir):
        omdb, tmdb, svc = self._build_service(cache_dir)
        sd = svc.get_series("Mini Show")

        assert sd.num_seasons == 2
        assert len(sd.seasons_list) == 2

        s1 = sd.seasons_list[0]
        assert s1.seasonID == 1
        assert s1.title == "Season 1"
        assert s1.num_episodes == 2
        assert len(s1.episodes_list) == 2

        ep = s1.episodes_list[0]
        assert ep.episodeId == 1
        assert ep.title == "S1E1"
        assert ep.year == 2020
        assert ep.runtime == 30
        assert ep.rating == 7.6           # rounded from vote_average 7.6
        assert ep.votes == 51
        assert ep.original_air_date == "2020-01-15"
        assert ep.plot.startswith("Plot for S1E1")

    def test_get_tv_season_called_for_each_season(self, cache_dir):
        omdb, tmdb, svc = self._build_service(cache_dir)
        svc.get_series("Mini Show")

        assert tmdb.get_tv_season.call_count == 2
        called = {c.args for c in tmdb.get_tv_season.call_args_list}
        assert called == {(4242, 1), (4242, 2)}

    def test_season_fetch_failure_is_skipped(self, cache_dir):
        """A single-season fetch error must not fail the whole series."""
        omdb = MagicMock(spec=OMDbClient)
        omdb.search_series.return_value = _omdb_result_from(omdb_series_breaking_bad())

        tmdb = MagicMock(spec=TMDbClient)
        tmdb.find_by_imdb_id.return_value = {"tv_id": 4242}
        tmdb.get_tv.return_value = _build_tmdb_clientside_tv(tmdb_tv_two_seasons())

        def season_side_effect(tv_id, n):
            if n == 1:
                raise TmdbNotFound("oops")
            return _build_tmdb_clientside_season(tmdb_season_payload(n, episodes=2))

        tmdb.get_tv_season.side_effect = season_side_effect

        sd = _make_service(omdb=omdb, tmdb=tmdb, tmp_cache=cache_dir).get_series("Mini Show")

        # season 1 dropped, season 2 retained
        assert len(sd.seasons_list) == 1
        assert sd.seasons_list[0].seasonID == 2

    def test_seasons_round_trip_through_cache(self, cache_dir):
        omdb, tmdb, svc = self._build_service(cache_dir)
        first = svc.get_series("Mini Show")

        # Second call: cache hit, no further TMDb calls.
        tmdb.reset_mock()
        second = svc.get_series("Mini Show")

        tmdb.find_by_imdb_id.assert_not_called()
        tmdb.get_tv.assert_not_called()
        tmdb.get_tv_season.assert_not_called()

        assert len(second.seasons_list) == len(first.seasons_list) == 2
        s1 = second.seasons_list[0]
        assert s1.num_episodes == 2
        assert s1.episodes_list[0].original_air_date == "2020-01-15"
        assert s1.episodes_list[1].title == "S1E2"
