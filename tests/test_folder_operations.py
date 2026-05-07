"""
Tests for fileOperations.py - folder name parsing and file operations.
"""
import pytest
from datetime import date
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

    def test_get_movie_name_from_folder_with_spaces_only(self):
        """Real-world: release name with spaces, no dots (the NOVI FILMOVI case)."""
        name, year = fileOperations.getMovieNameFromFolder("F1 2025 1080p WEB-DL")
        assert name == "F1"
        assert year == 2025

    def test_get_movie_name_from_folder_with_dashes(self):
        """Real-world: release name with dashes."""
        name, year = fileOperations.getMovieNameFromFolder("Sinners-2025-1080p-BluRay")
        assert name == "Sinners"
        assert year == 2025

    def test_get_movie_name_from_folder_mixed_separators(self):
        name, year = fileOperations.getMovieNameFromFolder("The Accountant 2.2025 1080p_WEB-DL")
        assert name == "The Accountant 2"
        assert year == 2025

    def test_get_movie_name_year_ceiling_lifted(self):
        """Year ceiling now follows the wall clock (was hardcoded to 2025)."""
        target = date.today().year
        name, year = fileOperations.getMovieNameFromFolder(f"Future.Movie.{target}.1080p")
        assert name == "Future Movie"
        assert year == target

    def test_get_movie_name_first_token_is_numeric_title(self):
        """Titles that ARE numbers ('300', '1917', '2012') still parse correctly."""
        name, year = fileOperations.getMovieNameFromFolder("300.2006.BluRay")
        assert name == "300"
        assert year == 2006

        name, year = fileOperations.getMovieNameFromFolder("1917.2019.1080p")
        assert name == "1917"
        assert year == 2019

    def test_get_movie_name_returns_empty_when_no_year(self):
        name, year = fileOperations.getMovieNameFromFolder("House of the Dragon")
        assert name == ""
        assert year == 0

    def test_series_release_with_season_marker_no_year(self):
        """Scene-style series releases without a year still yield a usable title.

        ``S01`` (and similar) acts as an end-of-title sentinel; the year is
        returned as 0 because the folder name doesn't carry one.
        """
        name, year = fileOperations.getMovieNameFromFolder(
            "Copenhagen.Cowboy.S01.COMPLETE.720p.NF.WEBRip.x264-GalaxyTV[TGx]"
        )
        assert name == "Copenhagen Cowboy"
        assert year == 0

    def test_series_release_with_episode_marker(self):
        name, year = fileOperations.getMovieNameFromFolder(
            "The.Last.Of.Us.S01E01.1080p.WEB.H264-CAKES"
        )
        assert name == "The Last Of Us"
        assert year == 0

    def test_series_release_with_short_season_token(self):
        name, year = fileOperations.getMovieNameFromFolder("Severance.S2.2160p.ATVP.WEB-DL")
        assert name == "Severance"
        assert year == 0

    def test_series_release_with_literal_season_word(self):
        name, year = fileOperations.getMovieNameFromFolder("Andor Season 2 1080p")
        assert name == "Andor"
        assert year == 0

    def test_year_wins_over_season_marker_when_both_present(self):
        """If a year appears before the season marker, it still parses as year."""
        name, year = fileOperations.getMovieNameFromFolder("Some.Show.2018.S01.1080p")
        assert name == "Some Show"
        assert year == 2018


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
