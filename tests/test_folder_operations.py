"""
Tests for fileOperations.py - folder name parsing and file operations.
"""
import pytest
from pathlib import Path
import fileOperations


@pytest.mark.unit
class TestFolderNameParsing:
    """Test folder name parsing functions."""
    
    def test_get_movie_name_from_folder_simple(self, test_movies_dir):
        """Test extracting movie name from simple folder."""
        # Function expects just the folder name, not full path
        folder_name = "The Accountant 2.2025"
        name, year = fileOperations.getMovieNameFromFolder(folder_name)
        # Function may add trailing spaces - normalize for comparison
        assert name.strip() == "The Accountant 2"
        assert year == 2025
    
    def test_get_movie_name_from_folder_with_quality_info(self, test_movies_dir):
        """Test extracting movie name from folder with quality indicators."""
        folder_path = test_movies_dir / "F1.2025. (1080p AMZN WEB-DL x265 10bit EAC3 5.1 Silence)"
        name, year = fileOperations.getMovieNameFromFolder(str(folder_path))
        # Function returns tuple (name, year)
        assert "F1" in name
        assert year == 2025
    
    def test_get_movie_name_from_folder_with_dots(self, test_movies_dir):
        """Test extracting movie name from folder with dots instead of spaces."""
        folder_path = test_movies_dir / "Sinners.2025.kkk"
        name, year = fileOperations.getMovieNameFromFolder(str(folder_path))
        # Function should handle dots
        assert "Sinners" in name
        assert year == 2025


@pytest.mark.unit
class TestYearExtraction:
    """Test year extraction from folder names."""
    
    def test_extract_year_standard_format(self):
        """Test extracting year from standard format - from IMDB folder name."""
        # This function expects folder name AFTER IMDb data is saved with format: "name (year) [imdbID] rating"
        folder_name = "The Accountant 2 (2025) [tt123456] 7.5"
        year = fileOperations.getYearFromIMDBFolderName(folder_name)
        assert year == 2025
    
    def test_get_name_year_from_folder(self):
        """Test parsing IMDB-formatted folder name to get movie name and year."""
        # This function expects IMDb-formatted folder names like "___MovieName  (2025) IMDB-9.5..."
        folder_name = "___Sinners  (2025) IMDB-9.1 Drama CAST - Michael B. Jordan"
        name, year = fileOperations.getNameYearFromNameWithIMDB(folder_name)
        assert "Sinners" in name
        assert year == "2025"  # Note: function returns year as string


@pytest.mark.integration
class TestFilePathHandling:
    """Test file path operations with real test data."""
    
    def test_sample_movie_folders_exist(self, sample_movie_folders):
        """Verify test data folders exist."""
        for folder in sample_movie_folders:
            assert folder.exists(), f"Test folder not found: {folder}"
    
    def test_can_read_folder_names(self, sample_movie_folders):
        """Test that we can read folder names from test data."""
        for folder in sample_movie_folders:
            result = fileOperations.getMovieNameFromFolder(str(folder))
            # Function returns tuple (name, year)
            assert result is not None
            name, year = result
            assert len(name) > 0
            assert year > 1930
