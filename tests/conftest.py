"""
Pytest configuration and shared fixtures for MoLiM tests.
"""
import pytest
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def test_data_dir():
    """Path to TestData directory with sample movies and series."""
    return Path(__file__).parent.parent / "TestData"


@pytest.fixture
def test_movies_dir(test_data_dir):
    """Path to TestData/Movies directory."""
    return test_data_dir / "Movies"


@pytest.fixture
def test_series_dir(test_data_dir):
    """Path to TestData/Series directory."""
    return test_data_dir / "Series"


@pytest.fixture
def sample_movie_folders(test_movies_dir):
    """List of sample movie folder paths."""
    return [
        test_movies_dir / "F1.2025. (1080p AMZN WEB-DL x265 10bit EAC3 5.1 Silence)",
        test_movies_dir / "Sinners.2025.kkk",
        test_movies_dir / "The Accountant 2.2025",
    ]


@pytest.fixture
def sample_series_folders(test_series_dir):
    """List of sample series folder paths."""
    return [
        test_series_dir / "House of the Dragon",
    ]
