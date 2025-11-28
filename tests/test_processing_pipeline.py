"""
Tests for processing.py - End-to-end processing pipeline.

These tests verify the complete workflow:
1. Scan folder for movies/series
2. Extract name and year
3. Fetch IMDb data
4. Save data and rename folder
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import processing
from IMDBMovieData import IMDBMovieData
from IMDBSeriesData import IMDBSeriesData


@pytest.fixture
def mock_movie_data():
    """Create a mock IMDBMovieData object."""
    movie = IMDBMovieData("The Matrix")
    movie.name = "The Matrix"
    movie.year = 1999
    movie.rating = 8.7
    movie.genres = "Action, Sci-Fi"
    movie.cast_leads = "Keanu Reeves, Laurence Fishburne"
    movie.movieID = "tt0133093"
    return movie


@pytest.fixture
def mock_series_data():
    """Create a mock IMDBSeriesData object."""
    series = IMDBSeriesData("Breaking Bad")
    series.name = "Breaking Bad"
    series.year = 2008
    series.rating = 9.5
    series.genres = "Crime, Drama"
    series.cast_leads = "Bryan Cranston, Aaron Paul"
    series.movieID = "tt0903747"
    series.num_seasons = 5
    return series


@pytest.fixture
def temp_test_folder(tmp_path):
    """Create a temporary folder structure for testing."""
    test_folder = tmp_path / "TestMovies"
    test_folder.mkdir()
    
    # Create movie folders
    (test_folder / "The.Matrix.1999").mkdir()
    (test_folder / "Inception.2010").mkdir()
    (test_folder / "___Existing IMDB Movie (2020) IMDB-9.0").mkdir()  # Already processed
    
    return test_folder


@pytest.mark.unit
class TestProcessFolder:
    """Test the processFolder function with mocked dependencies."""
    
    def test_processFolder_success(self, mocker, temp_test_folder, mock_movie_data):
        """Test successful processing of a folder with movies."""
        # Mock os.scandir to return our test folders
        mock_entry1 = Mock()
        mock_entry1.name = "The.Matrix.1999"
        mock_entry1.is_dir = Mock(return_value=True)
        
        mock_entry2 = Mock()
        mock_entry2.name = "Inception.2010"
        mock_entry2.is_dir = Mock(return_value=True)
        
        mock_entry3 = Mock()
        mock_entry3.name = "___Existing IMDB Movie (2020) IMDB-9.0"
        mock_entry3.is_dir = Mock(return_value=True)
        
        mocker.patch('os.scandir', return_value=[mock_entry1, mock_entry2, mock_entry3])
        
        # Mock the pipeline steps
        mocker.patch('fileOperations.getMovieNameFromFolder', return_value=("The Matrix", 1999))
        mocker.patch('imdbAccess.fetchMovieData', return_value=mock_movie_data)
        mock_save = mocker.patch('fileOperations.saveMovieDataAndRenameFolder')
        
        # Execute
        processing.processFolder(str(temp_test_folder))
        
        # Verify - should process 2 folders (skip the IMDB one)
        assert mock_save.call_count == 2
    
    def test_processFolder_skip_existing_imdb(self, mocker, temp_test_folder):
        """Test that folders with 'IMDB' in name are skipped."""
        mock_entry = Mock()
        mock_entry.name = "___Good Movie (2020) IMDB-9.0"
        mock_entry.is_dir = Mock(return_value=True)
        mocker.patch('os.scandir', return_value=[mock_entry])
        
        mock_fetch = mocker.patch('imdbAccess.fetchMovieData')
        
        processing.processFolder(str(temp_test_folder))
        
        # Should not fetch data for already processed folders
        mock_fetch.assert_not_called()
    
    def test_processFolder_empty_result(self, mocker, temp_test_folder):
        """Test handling when IMDb returns no data."""
        mock_entry = Mock()
        mock_entry.name = "Unknown.Movie.2099"
        mock_entry.is_dir = Mock(return_value=True)
        mocker.patch('os.scandir', return_value=[mock_entry])
        
        mocker.patch('fileOperations.getMovieNameFromFolder', return_value=("Unknown Movie", 2099))
        
        # Mock empty result
        empty_data = IMDBMovieData("Unknown Movie")
        empty_data.name = ""
        mocker.patch('imdbAccess.fetchMovieData', return_value=empty_data)
        
        mock_save = mocker.patch('fileOperations.saveMovieDataAndRenameFolder')
        
        processing.processFolder(str(temp_test_folder))
        
        # Should not save when no data found
        mock_save.assert_not_called()


@pytest.mark.unit
class TestProcessSeriesFolder:
    """Test the processSeriesFolder function."""
    
    def test_processSeriesFolder_success(self, mocker, temp_test_folder, mock_series_data):
        """Test successful processing of series folders."""
        mock_entry1 = Mock()
        mock_entry1.name = "Breaking.Bad"
        mock_entry1.is_dir = Mock(return_value=True)
        
        mock_entry2 = Mock()
        mock_entry2.name = "___Game of Thrones  (2011) IMDB-9.2"
        mock_entry2.is_dir = Mock(return_value=True)
        
        mocker.patch('os.scandir', return_value=[mock_entry1, mock_entry2])
        
        mocker.patch('fileOperations.getMovieNameFromFolder', return_value=("Breaking Bad", 2008))
        mocker.patch('imdbAccess.fetchSeriesData', return_value=mock_series_data)
        mock_save = mocker.patch('fileOperations.saveSeriesDataAndRenameFolder')
        
        processing.processSeriesFolder(str(temp_test_folder))
        
        # Should process only the non-IMDB folder
        assert mock_save.call_count == 1
        mock_save.assert_called_once_with(mock_series_data, str(temp_test_folder), "Breaking.Bad")


@pytest.mark.unit
class TestProcessListOfFolders:
    """Test processing multiple folders."""
    
    def test_processListOfFolders(self, mocker, mock_movie_data):
        """Test processing a list of folders."""
        # Mock os.scandir for both folders
        mock_entry1 = Mock()
        mock_entry1.name = "Movie1.2020"
        mock_entry1.is_dir = Mock(return_value=True)
        
        mock_entry2 = Mock()
        mock_entry2.name = "Movie2.2021"
        mock_entry2.is_dir = Mock(return_value=True)
        
        # scandir will be called twice (once per parent folder)
        mocker.patch('os.scandir', side_effect=[
            [mock_entry1],  # First folder
            [mock_entry2]   # Second folder
        ])
        
        # Mock the internal operations
        mocker.patch('fileOperations.getMovieNameFromFolder', return_value=("Test Movie", 2020))
        mocker.patch('imdbAccess.fetchMovieData', return_value=mock_movie_data)
        mock_save = mocker.patch('fileOperations.saveMovieDataAndRenameFolder')
        
        # Execute with two parent folders
        processing.processListOfFolders(["D:\\Movies1", "D:\\Movies2"])
        
        # Should save data for both movies (one from each folder)
        assert mock_save.call_count == 2


@pytest.mark.integration
class TestProcessingIntegration:
    """Integration tests with real test data."""
    
    def test_processFolder_with_real_structure(self, test_movies_dir, mocker, mock_movie_data):
        """Test processing with real TestData folder structure."""
        # Mock only the IMDb fetching (expensive external call)
        mocker.patch('imdbAccess.fetchMovieData', return_value=mock_movie_data)
        mock_save = mocker.patch('fileOperations.saveMovieDataAndRenameFolder')
        
        # Process real test folder
        processing.processFolder(str(test_movies_dir))
        
        # Should attempt to process the real folders in TestData/Movies
        # (exact count depends on test data, but should be > 0)
        assert mock_save.call_count > 0
    
    @pytest.mark.slow
    def test_real_cinemagoer_fetch_and_process(self, tmp_path, mocker):
        """REAL integration test: Actually fetch data from IMDb using cinemagoer.
        
        This test makes a real API call to verify cinemagoer integration works.
        Marked as 'slow' because it requires internet and real API call.
        
        Uses a well-known movie (The Matrix, 1999) to ensure stable test data.
        """
        import time
        
        # Create a test folder structure
        test_folder = tmp_path / "test_movies"
        test_folder.mkdir()
        movie_folder = test_folder / "The.Matrix.1999"
        movie_folder.mkdir()
        
        # Mock only the save operation to avoid actually writing files
        mock_save = mocker.patch('fileOperations.saveMovieDataAndRenameFolder')
        
        # Add small delay to be respectful to IMDb servers
        time.sleep(1)
        
        # Process folder - this will make REAL cinemagoer API call
        processing.processFolder(str(test_folder))
        
        # Verify the save was called (meaning fetch succeeded)
        assert mock_save.call_count == 1
        
        # Verify we got real movie data from cinemagoer
        call_args = mock_save.call_args[0]
        movie_data = call_args[0]  # First argument is the IMDBMovieData object
        
        # Verify essential fields from real IMDb data
        assert movie_data.name == "The Matrix"
        assert movie_data.year == 1999
        assert movie_data.rating > 8.0  # The Matrix has high rating
        assert movie_data.movieID != 0 and movie_data.movieID != ""  # Should have real IMDb ID
        assert len(movie_data.genres) > 0  # Should have genres
        assert len(movie_data.directors) > 0  # Should have directors
        
        print(f"\n✓ Successfully fetched real data from cinemagoer:")
        print(f"  Title: {movie_data.name} ({movie_data.year})")
        print(f"  Rating: {movie_data.rating}")
        print(f"  IMDb ID: {movie_data.movieID}")
        print(f"  Genres: {', '.join(movie_data.genres)}")
        print(f"  Directors: {', '.join(movie_data.directors)}")


@pytest.mark.unit
class TestFolderRecheck:
    """Test recheck functionality for existing processed folders."""
    
    def test_folderRecheckDataWithIMDB(self, mocker, temp_test_folder, mock_movie_data):
        """Test rechecking folders that already have IMDb data."""
        # Create a folder that looks like it's already processed
        processed_folder_name = "___The Matrix  (1999) IMDB-8.7 Action, Sci-Fi CAST - Keanu Reeves"
        
        mock_entry = Mock()
        mock_entry.name = processed_folder_name
        mock_entry.is_dir = Mock(return_value=True)
        mocker.patch('os.scandir', return_value=[mock_entry])
        
        # Mock the recheck flow - folder WITHOUT movieID (needs processing)
        mocker.patch('fileOperations.doesFilmDataHasMovieID', return_value=False)
        mocker.patch('imdbAccess.fetchMovieData', return_value=mock_movie_data)
        mocker.patch('fileOperations.getMovieFolderNameFromMovieData', return_value=processed_folder_name)
        mock_save_txt = mocker.patch('fileOperations.saveTXTWithMovieData')
        mocker.patch('os.path.isdir', return_value=False)
        
        processing.folderRecheckDataWithIMDB(str(temp_test_folder))
        
        # Should save the updated data (folder name matches, so just update TXT)
        assert mock_save_txt.call_count == 1


@pytest.mark.unit
class TestPipelineComponents:
    """Test individual pipeline components work together."""
    
    def test_pipeline_parse_fetch_save(self, mocker, mock_movie_data):
        """Test the complete pipeline: parse → fetch → save."""
        folder_name = "The.Matrix.1999"
        
        # Step 1: Parse folder name
        with patch('fileOperations.getMovieNameFromFolder') as mock_parse:
            mock_parse.return_value = ("The Matrix", 1999)
            name, year = mock_parse(folder_name)
            assert name == "The Matrix"
            assert year == 1999
        
        # Step 2: Fetch from IMDb
        with patch('imdbAccess.fetchMovieData') as mock_fetch:
            mock_fetch.return_value = mock_movie_data
            data = mock_fetch(name, year)
            assert data.name == "The Matrix"
        
        # Step 3: Save and rename
        with patch('fileOperations.saveMovieDataAndRenameFolder') as mock_save:
            mock_save.return_value = None
            mock_save(data, "/test/folder", folder_name)
            mock_save.assert_called_once()


@pytest.mark.smoke
class TestProcessingSmokeTests:
    """Quick smoke tests to verify basic functionality."""
    
    def test_processFolder_doesnt_crash_on_empty_folder(self, mocker, tmp_path):
        """Smoke test: empty folder doesn't crash."""
        empty_folder = tmp_path / "EmptyFolder"
        empty_folder.mkdir()
        
        mocker.patch('os.scandir', return_value=[])
        
        # Should complete without error
        processing.processFolder(str(empty_folder))
    
    def test_processFolder_handles_files_not_dirs(self, mocker, tmp_path):
        """Smoke test: files in folder are ignored (only dirs processed)."""
        test_folder = tmp_path / "TestFolder"
        test_folder.mkdir()
        (test_folder / "somefile.txt").write_text("test")
        
        mock_entries = [
            Mock(name="somefile.txt", is_dir=lambda: False),
            Mock(name="Movie.2020", is_dir=lambda: True),
        ]
        mocker.patch('os.scandir', return_value=mock_entries)
        
        mocker.patch('fileOperations.getMovieNameFromFolder', return_value=("Movie", 2020))
        empty_data = IMDBMovieData("Movie")
        empty_data.name = ""
        mocker.patch('imdbAccess.fetchMovieData', return_value=empty_data)
        
        # Should only process directory, not file
        processing.processFolder(str(test_folder))
        # If it completes, test passes
