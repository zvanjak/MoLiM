"""External data clients (OMDb, TMDb) and the movie data service.

This package replaces the cinemagoer-based imdbAccess module with a
hybrid that combines OMDb (ratings, vote counts, IMDb canonical ID)
with TMDb (rich metadata, cast, crew, posters).

See REFACTORING_PLAN.md and beads epic MoLiM-02x for context.
"""

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
    TmdbNotFound,
    TmdbCredits,
    TmdbMovie,
    TmdbTv,
)
from molim_data.movie_data_service import MovieDataService

__all__ = [
    "OMDbClient",
    "OmdbAuthError",
    "OmdbError",
    "OmdbNotFound",
    "OmdbResult",
    "TMDbClient",
    "TmdbAuthError",
    "TmdbError",
    "TmdbNotFound",
    "TmdbCredits",
    "TmdbMovie",
    "TmdbTv",
    "MovieDataService",
]
