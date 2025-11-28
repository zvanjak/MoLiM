"""
Tests for imdbAccess.py - IMDb metadata fetching.

These tests include both unit tests with mocked API responses
and integration tests with the real IMDb API (marked as @slow).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import imdbAccess
from IMDBMovieData import IMDBMovieData
from IMDBSeriesData import IMDBSeriesData


@pytest.mark.unit
class TestMovieDataFetching:
    """Test movie data fetching with mocked IMDb responses."""
    
    def test_fetchMovieData_success_mock(self, mocker):
        """Test successful movie data fetch with mocked cinemagoer."""
        # Mock the search results
        mock_movie = Mock()
        mock_movie.movieID = "tt123456"
        mock_movie.data = {
            'title': 'The Matrix',
            'year': 1999,
            'kind': 'movie'
        }
        
        # Mock the detailed movie data
        mock_detailed = Mock()
        mock_detailed.data = {
            'title': 'The Matrix',
            'year': 1999,
            'rating': 8.7,
            'genres': ['Action', 'Sci-Fi'],
            'cast': [{'name': 'Keanu Reeves'}, {'name': 'Laurence Fishburne'}],
            'director': [{'name': 'Wachowski Brothers'}]
        }
        
        # Patch cinemagoer functions
        mocker.patch('imdbAccess.ia.search_movie', return_value=[mock_movie])
        mocker.patch('imdbAccess.ia.get_movie', return_value=mock_detailed)
        mocker.patch('time.sleep')  # Skip sleep delays in tests
        mocker.patch('random.randrange', return_value=0)  # Consistent delay
        
        result = imdbAccess.fetchMovieData('The Matrix', 1999)
        
        assert result is not None
        assert result.name == 'The Matrix'
    
    def test_fetchMovieData_no_results_mock(self, mocker):
        """Test handling of no search results."""
        mocker.patch('imdbAccess.ia.search_movie', return_value=[])
        mocker.patch('time.sleep')
        
        result = imdbAccess.fetchMovieData('NonexistentMovie9999', 2999)
        
        assert result.name == ""
    
    def test_fetchMovieData_network_error_mock(self, mocker):
        """Test handling of network errors."""
        mocker.patch('imdbAccess.ia.search_movie', side_effect=Exception("Network error"))
        mocker.patch('time.sleep')
        
        result = imdbAccess.fetchMovieData('Test Movie', 2020)
        
        assert result.name == ""


@pytest.mark.unit
class TestSeriesDataFetching:
    """Test series data fetching with mocked IMDb responses."""
    
    def test_fetchSeriesData_success_mock(self, mocker):
        """Test successful series data fetch with mocked cinemagoer."""
        # Mock the search results for series
        mock_series = Mock()
        mock_series.movieID = "tt987654"
        mock_series.data = {
            'title': 'Breaking Bad',
            'year': 2008,
            'kind': 'tv series'
        }
        
        # Mock the detailed series data
        mock_detailed = Mock()
        mock_detailed.data = {
            'title': 'Breaking Bad',
            'year': 2008,
            'rating': 9.5,
            'genres': ['Crime', 'Drama'],
            'cast': [{'name': 'Bryan Cranston'}, {'name': 'Aaron Paul'}],
            'seasons': ['1', '2', '3', '4', '5']
        }
        
        mocker.patch('imdbAccess.ia.search_movie', return_value=[mock_series])
        mocker.patch('imdbAccess.ia.get_movie', return_value=mock_detailed)
        mocker.patch('imdbAccess.ia.update', return_value=None)
        mocker.patch('time.sleep')
        mocker.patch('random.randrange', return_value=0)
        
        result = imdbAccess.fetchSeriesData('Breaking Bad')
        
        assert result is not None
        assert result.name == 'Breaking Bad'


@pytest.mark.slow
@pytest.mark.integration
class TestRealIMDbAPI:
    """Integration tests with real IMDb API - marked as slow."""
    
    @pytest.mark.skip(reason="Real API call - enable manually when needed")
    def test_fetchMovieData_real_api(self):
        """Test fetching real movie data from IMDb (skipped by default)."""
        # This test makes a real API call - only run when explicitly needed
        result = imdbAccess.fetchMovieData('The Matrix', 1999)
        
        assert result is not None
        assert 'Matrix' in result.name
        assert result.rating > 0
    
    @pytest.mark.skip(reason="Real API call - enable manually when needed")
    def test_fetchSeriesData_real_api(self):
        """Test fetching real series data from IMDb (skipped by default)."""
        # This test makes a real API call - only run when explicitly needed
        result = imdbAccess.fetchSeriesData('Breaking Bad')
        
        assert result is not None
        assert 'Breaking Bad' in result.name
        assert result.rating > 0


@pytest.mark.unit
class TestIMDbDataStructures:
    """Test IMDb data structure creation and validation."""
    
    def test_movie_data_initialization(self):
        """Test IMDBMovieData initialization."""
        movie = IMDBMovieData("Test Movie")
        
        assert movie.name == "Test Movie"
        # Check default values are set
        assert hasattr(movie, 'rating')
        assert hasattr(movie, 'year')
    
    def test_series_data_initialization(self):
        """Test IMDBSeriesData initialization."""
        series = IMDBSeriesData("Test Series")
        
        assert series.name == "Test Series"
        # Check default values are set
        assert hasattr(series, 'rating')
        assert hasattr(series, 'year')
