# MoLiM Refactoring Plan
## Transforming from Script to Application

---

## 🎯 Goals

1. **Separate Concerns**: Clear boundaries between data, business logic, and presentation
2. **Database Migration**: Move from text files to SQLite
3. **Modern Python**: Type hints, dataclasses, async/await
4. **GUI Ready**: Architecture that supports Tkinter UI
5. **Testable**: Unit tests for all core functionality
6. **Maintainable**: Clear structure, documentation, logging

---

## 📅 Phase 1: Foundation & Cleanup (Week 1-2)

### Step 1.1: Fix Immediate Issues
**Priority: Critical**

```python
# Fix invalid escape sequences in myFolders.py and MoLiM.py
# BEFORE:
"Z:\Movies\FILMOVI\___Al Pacino"

# AFTER:
r"Z:\Movies\FILMOVI\___Al Pacino"
# OR
"Z:\\Movies\\FILMOVI\\___Al Pacino"
```

**Tasks:**
- [ ] Fix all string escape sequences (use raw strings)
- [ ] Remove all commented-out code from MoLiM.py
- [ ] Create `.gitignore` improvements (ignore Data/ folder)

### Step 1.2: Create Configuration System
**Priority: High**

Create `config.yaml`:
```yaml
# Application Settings
app:
  name: "MoLiM"
  version: "2.0.0"

# Paths Configuration
paths:
  base_folder: "Z:/Movies/FILMOVI"
  processing_folders:
    new_movies: "E:/NOVI FILMOVI"
    new_series: "E:/NOVE SERIJE"
  
  # Category Folders
  directors: "Z:/Movies/FILMOVI/__00_Directors_others"
  actors: "Z:/Movies/FILMOVI/___00_Actors_others"

# IMDb Settings
imdb:
  rate_limit_seconds: 5
  rate_limit_variance: 5
  retry_attempts: 3
  timeout_seconds: 30

# Rating Thresholds
ratings:
  masterpiece: 9.0
  excellent: 8.0
  good: 7.0
  poor: 6.0

# Logging
logging:
  level: "INFO"
  file: "logs/molim.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

Create `molim/utils/config.py`:
```python
from typing import Dict, Any
import yaml
from pathlib import Path

class Config:
    """Application configuration manager."""
    
    _instance = None
    _config: Dict[str, Any] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, config_path: str = "config.yaml") -> None:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

# Global config instance
config = Config()
```

**Tasks:**
- [ ] Create `config.yaml` with all paths and settings
- [ ] Create `Config` class with singleton pattern
- [ ] Install PyYAML: `pip install pyyaml`
- [ ] Update `requirements.txt`
- [ ] Refactor hardcoded paths to use config

### Step 1.3: Setup Logging
**Priority: High**

Create `molim/utils/logging_config.py`:
```python
import logging
import logging.handlers
from pathlib import Path
from .config import config

def setup_logging() -> logging.Logger:
    """Configure application logging."""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get logging configuration
    log_level = config.get('logging.level', 'INFO')
    log_file = config.get('logging.file', 'logs/molim.log')
    log_format = config.get('logging.format', 
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Configure root logger
    logger = logging.getLogger('molim')
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logging()
```

**Tasks:**
- [ ] Create logging configuration
- [ ] Replace all `print()` statements with `logger.info()`, `logger.error()`, etc.
- [ ] Add debug logging for important operations

### Step 1.4: Create Project Structure
**Priority: High**

```
d:\Projects\MoLiM\
├── molim/                      # Main package
│   ├── __init__.py
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── models/            # Data models
│   │   │   ├── __init__.py
│   │   │   ├── movie.py
│   │   │   ├── series.py
│   │   │   └── person.py
│   │   ├── repositories/      # Data access
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── movie_repository.py
│   │   │   └── series_repository.py
│   │   └── services/          # Business logic
│   │       ├── __init__.py
│   │       ├── imdb_service.py
│   │       ├── processing_service.py
│   │       └── statistics_service.py
│   ├── infrastructure/        # External dependencies
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   └── migrations/
│   │   └── imdb/
│   │       ├── __init__.py
│   │       └── client.py
│   ├── ui/                    # User interfaces
│   │   ├── __init__.py
│   │   ├── cli/              # Command-line interface
│   │   │   ├── __init__.py
│   │   │   └── commands.py
│   │   └── gui/              # Tkinter GUI
│   │       ├── __init__.py
│   │       ├── main_window.py
│   │       ├── widgets/
│   │       └── viewmodels/
│   └── utils/                 # Utilities
│       ├── __init__.py
│       ├── config.py
│       ├── logging_config.py
│       ├── validators.py
│       └── constants.py
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── scripts/                   # Utility scripts
│   ├── migrate_to_db.py
│   └── backup_data.py
├── logs/                      # Log files
├── data/                      # Database file
├── legacy/                    # Old code (for reference)
│   ├── MoLiM_old.py
│   ├── processing_old.py
│   └── ...
├── config.yaml               # Configuration
├── requirements.txt          # Dependencies
├── setup.py                  # Package setup
├── README.md
├── OVERVIEW.md
└── REFACTORING_PLAN.md
```

**Tasks:**
- [ ] Create new directory structure
- [ ] Move old files to `legacy/` folder
- [ ] Create all `__init__.py` files
- [ ] Setup `setup.py` for package installation

---

## 📅 Phase 2: Data Layer (Week 3-4)

### Step 2.1: Define Modern Data Models
**Priority: Critical**

Create `molim/core/models/movie.py`:
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class Movie:
    """Movie data model."""
    
    # Identity
    id: Optional[int] = None
    name: str = ""
    imdb_name: str = ""
    imdb_id: str = ""
    
    # Basic Info
    year: int = 0
    runtime: int = 0  # minutes
    rating: float = 0.0
    votes: int = 0
    
    # Classification
    genres: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    
    # People
    directors: List[str] = field(default_factory=list)
    producers: List[str] = field(default_factory=list)
    writers: List[str] = field(default_factory=list)
    cast: List[str] = field(default_factory=list)
    
    # Additional Info
    plot: str = ""
    box_office: Optional[dict] = None
    top_250_rank: Optional[int] = None
    release_date: Optional[datetime] = None
    
    # Metadata
    folder_path: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def is_directed_by(self, director: str) -> bool:
        """Check if movie is directed by given director."""
        return any(director.lower() in d.lower() for d in self.directors)
    
    def has_genre(self, genre: str) -> bool:
        """Check if movie has given genre."""
        return any(genre.lower() in g.lower() for g in self.genres)
    
    def has_actor(self, actor: str) -> bool:
        """Check if movie has given actor."""
        return any(actor.lower() in a.lower() for a in self.cast[:10])
    
    def get_rating_category(self) -> str:
        """Get rating category for folder naming."""
        if self.rating >= 9.0:
            return "masterpiece"
        elif self.rating >= 8.0:
            return "excellent"
        elif self.rating >= 7.0:
            return "good"
        elif self.rating < 6.0:
            return "poor"
        else:
            return "average"
    
    def get_folder_prefix(self) -> str:
        """Get folder name prefix based on rating."""
        category = self.get_rating_category()
        return {
            "masterpiece": "___",
            "excellent": "__",
            "good": "_",
            "poor": "zzz_",
            "average": ""
        }.get(category, "")
```

Create `molim/core/models/series.py` (similar structure for TV series)

**Tasks:**
- [ ] Create `Movie` dataclass with all fields
- [ ] Create `Series` dataclass
- [ ] Create `Season` and `Episode` dataclasses
- [ ] Add validation methods
- [ ] Add convenience methods (is_directed_by, etc.)

### Step 2.2: Database Schema Design
**Priority: Critical**

Create `molim/infrastructure/database/schema.sql`:
```sql
-- Movies Table
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    imdb_name TEXT,
    imdb_id TEXT UNIQUE,
    year INTEGER,
    runtime INTEGER,
    rating REAL,
    votes INTEGER,
    plot TEXT,
    box_office TEXT,
    top_250_rank INTEGER,
    release_date TEXT,
    folder_path TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- People Table (Directors, Actors, Writers, Producers)
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL  -- 'director', 'actor', 'writer', 'producer'
);

-- Movie-Person Relationships
CREATE TABLE IF NOT EXISTS movie_people (
    movie_id INTEGER,
    person_id INTEGER,
    role TEXT NOT NULL,  -- 'director', 'actor', 'writer', 'producer'
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, person_id, role)
);

-- Genres Table
CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Movie-Genre Relationships
CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id INTEGER,
    genre_id INTEGER,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

-- Series Table
CREATE TABLE IF NOT EXISTS series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    imdb_name TEXT,
    imdb_id TEXT UNIQUE,
    year INTEGER,
    num_seasons INTEGER,
    runtime INTEGER,
    rating REAL,
    votes INTEGER,
    plot TEXT,
    folder_path TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Seasons Table
CREATE TABLE IF NOT EXISTS seasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id INTEGER,
    season_number INTEGER,
    num_episodes INTEGER,
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE
);

-- Episodes Table
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id INTEGER,
    episode_number INTEGER,
    title TEXT,
    rating REAL,
    votes INTEGER,
    air_date TEXT,
    year INTEGER,
    plot TEXT,
    FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_movies_rating ON movies(rating);
CREATE INDEX IF NOT EXISTS idx_movies_year ON movies(year);
CREATE INDEX IF NOT EXISTS idx_movies_imdb_id ON movies(imdb_id);
CREATE INDEX IF NOT EXISTS idx_people_name ON people(name);
CREATE INDEX IF NOT EXISTS idx_genres_name ON genres(name);
```

**Tasks:**
- [ ] Design normalized database schema
- [ ] Create migration scripts
- [ ] Create database connection manager
- [ ] Add indexes for performance

### Step 2.3: Repository Pattern Implementation
**Priority: High**

Create `molim/core/repositories/base.py`:
```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    """Base repository interface."""
    
    @abstractmethod
    def add(self, entity: T) -> T:
        """Add new entity."""
        pass
    
    @abstractmethod
    def get(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all entities."""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Update existing entity."""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    def find(self, **criteria) -> List[T]:
        """Find entities matching criteria."""
        pass
```

Create `molim/core/repositories/movie_repository.py`:
```python
import sqlite3
from typing import Optional, List
from ..models.movie import Movie
from .base import Repository

class MovieRepository(Repository[Movie]):
    """SQLite-based movie repository."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def add(self, movie: Movie) -> Movie:
        """Add new movie to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO movies (name, imdb_name, imdb_id, year, runtime, 
                                  rating, votes, plot, folder_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (movie.name, movie.imdb_name, movie.imdb_id, movie.year,
                  movie.runtime, movie.rating, movie.votes, movie.plot,
                  movie.folder_path))
            movie.id = cursor.lastrowid
            conn.commit()
        return movie
    
    def find_by_rating_and_director(self, min_rating: float, 
                                    director: str) -> List[Movie]:
        """Find movies by minimum rating and director."""
        # Implementation with JOIN to movie_people table
        pass
    
    # ... other methods
```

**Tasks:**
- [ ] Create base repository interface
- [ ] Implement MovieRepository
- [ ] Implement SeriesRepository
- [ ] Add complex query methods
- [ ] Add transaction support

### Step 2.4: Migration Script from Text Files to Database
**Priority: High**

Create `scripts/migrate_to_db.py`:
```python
"""Migrate existing text file data to SQLite database."""

import sys
from pathlib import Path
from molim.utils.config import config
from molim.core.repositories.movie_repository import MovieRepository
from molim.infrastructure.database.connection import init_database

# Import legacy file operations
sys.path.append('legacy')
import fileOperations
import IMDBMovieData

def migrate_movies():
    """Migrate all movies from text files to database."""
    logger.info("Starting migration...")
    
    repo = MovieRepository(config.get('database.path'))
    
    # Iterate through all movie folders
    # Load text files using old fileOperations
    # Convert to new Movie model
    # Save to database via repository
    
    logger.info("Migration complete!")

if __name__ == "__main__":
    migrate_movies()
```

**Tasks:**
- [ ] Create migration script
- [ ] Test on backup data
- [ ] Verify data integrity
- [ ] Create rollback mechanism

---

## 📅 Phase 3: Business Logic Layer (Week 5-6)

### Step 3.1: IMDb Service
**Priority: High**

Create `molim/core/services/imdb_service.py`:
```python
from typing import Optional
import asyncio
from imdb import Cinemagoer
from ..models.movie import Movie
from ...utils.logging_config import logger
from ...utils.config import config

class IMDbService:
    """Service for fetching data from IMDb."""
    
    def __init__(self):
        self.ia = Cinemagoer()
        self.rate_limit = config.get('imdb.rate_limit_seconds', 5)
    
    async def fetch_movie(self, name: str, year: int) -> Optional[Movie]:
        """Fetch movie data from IMDb."""
        try:
            logger.info(f"Fetching movie: {name} ({year})")
            
            # Search for movie
            results = await asyncio.to_thread(self.ia.search_movie, name)
            
            if not results:
                logger.warning(f"No results found for {name}")
                return None
            
            # Find exact match
            movie_id = self._find_exact_match(results, name, year)
            
            if movie_id:
                return await self.fetch_movie_by_id(name, movie_id)
            
            logger.warning(f"No exact match for {name} ({year})")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching movie {name}: {e}")
            return None
    
    async def fetch_movie_by_id(self, name: str, imdb_id: str) -> Optional[Movie]:
        """Fetch movie by IMDb ID."""
        # Implementation
        pass
    
    def _find_exact_match(self, results, name, year):
        """Find exact match in search results."""
        # Implementation
        pass
```

**Tasks:**
- [ ] Create IMDbService class
- [ ] Implement async movie fetching
- [ ] Implement series fetching
- [ ] Add retry logic
- [ ] Add rate limiting
- [ ] Add error handling

### Step 3.2: Processing Service
**Priority: High**

Create `molim/core/services/processing_service.py`:
```python
from pathlib import Path
from typing import List, Callable
from ..models.movie import Movie
from ..repositories.movie_repository import MovieRepository
from .imdb_service import IMDbService
from ...utils.logging_config import logger

class ProcessingService:
    """Service for processing movie folders."""
    
    def __init__(self, movie_repo: MovieRepository, imdb_service: IMDbService):
        self.movie_repo = movie_repo
        self.imdb_service = imdb_service
    
    async def process_folder(self, folder_path: str, 
                            progress_callback: Optional[Callable] = None):
        """
        Process all movies in a folder.
        
        Args:
            folder_path: Path to folder containing movies
            progress_callback: Optional callback for progress updates
        """
        folder = Path(folder_path)
        subfolders = [f for f in folder.iterdir() if f.is_dir()]
        
        total = len(subfolders)
        processed = 0
        
        for subfolder in subfolders:
            if "IMDB" not in subfolder.name:
                logger.info(f"Processing: {subfolder.name}")
                
                # Extract movie name and year
                name, year = self._parse_folder_name(subfolder.name)
                
                # Fetch from IMDb
                movie = await self.imdb_service.fetch_movie(name, year)
                
                if movie:
                    # Save to database
                    movie.folder_path = str(subfolder)
                    self.movie_repo.add(movie)
                    
                    # Rename folder with metadata
                    await self._rename_folder(subfolder, movie)
                
                processed += 1
                if progress_callback:
                    progress_callback(processed, total)
    
    def _parse_folder_name(self, folder_name: str) -> tuple[str, int]:
        """Parse movie name and year from folder name."""
        # Implementation
        pass
    
    async def _rename_folder(self, old_path: Path, movie: Movie):
        """Rename folder with IMDb metadata."""
        # Implementation
        pass
```

**Tasks:**
- [ ] Create ProcessingService
- [ ] Implement folder processing
- [ ] Add progress tracking
- [ ] Implement folder renaming
- [ ] Add validation

### Step 3.3: Statistics Service
**Priority: Medium**

Create `molim/core/services/statistics_service.py`:
```python
from typing import Dict, List
from ..repositories.movie_repository import MovieRepository
from ..models.movie import Movie

class StatisticsService:
    """Service for generating statistics."""
    
    def __init__(self, movie_repo: MovieRepository):
        self.movie_repo = movie_repo
    
    def get_rating_distribution(self) -> Dict[str, int]:
        """Get count of movies by rating category."""
        movies = self.movie_repo.get_all()
        distribution = {
            "masterpiece": 0,
            "excellent": 0,
            "good": 0,
            "average": 0,
            "poor": 0
        }
        for movie in movies:
            category = movie.get_rating_category()
            distribution[category] += 1
        return distribution
    
    def get_top_directors(self, limit: int = 10) -> List[tuple[str, float]]:
        """Get top directors by average rating of top 10 movies."""
        # Implementation with SQL query
        pass
    
    def get_decade_distribution(self) -> Dict[int, int]:
        """Get count of movies by decade."""
        # Implementation
        pass
```

**Tasks:**
- [ ] Create StatisticsService
- [ ] Implement rating distribution
- [ ] Implement director statistics
- [ ] Implement actor statistics
- [ ] Implement genre statistics

---

## 📅 Phase 4: CLI Interface (Week 7)

### Step 4.1: Command-Line Interface
**Priority: High**

Create `molim/ui/cli/commands.py`:
```python
import click
from ...core.services import ProcessingService, StatisticsService
from ...core.repositories import MovieRepository
from ...infrastructure.database import init_database
from ...utils.config import config
from ...utils.logging_config import logger

@click.group()
def cli():
    """MoLiM - Movie Library Manager"""
    pass

@cli.command()
@click.argument('folder_path')
def process(folder_path):
    """Process movies in a folder."""
    logger.info(f"Processing folder: {folder_path}")
    
    # Initialize services
    db_path = config.get('database.path')
    movie_repo = MovieRepository(db_path)
    imdb_service = IMDbService()
    processing_service = ProcessingService(movie_repo, imdb_service)
    
    # Process folder
    import asyncio
    asyncio.run(processing_service.process_folder(folder_path))
    
    logger.info("Processing complete!")

@cli.command()
def stats():
    """Show collection statistics."""
    db_path = config.get('database.path')
    movie_repo = MovieRepository(db_path)
    stats_service = StatisticsService(movie_repo)
    
    # Show statistics
    distribution = stats_service.get_rating_distribution()
    click.echo("Rating Distribution:")
    for category, count in distribution.items():
        click.echo(f"  {category}: {count}")

@cli.command()
@click.option('--director', help='Director name')
@click.option('--actor', help='Actor name')
@click.option('--genre', help='Genre')
@click.option('--min-rating', type=float, default=7.0, help='Minimum rating')
def search(director, actor, genre, min_rating):
    """Search for movies."""
    db_path = config.get('database.path')
    movie_repo = MovieRepository(db_path)
    
    # Build search criteria
    criteria = {'min_rating': min_rating}
    if director:
        criteria['director'] = director
    if actor:
        criteria['actor'] = actor
    if genre:
        criteria['genre'] = genre
    
    # Search
    movies = movie_repo.find(**criteria)
    
    # Display results
    for movie in movies:
        click.echo(f"{movie.name} ({movie.year}) - {movie.rating}")

if __name__ == '__main__':
    cli()
```

Create `main.py`:
```python
"""Main entry point for MoLiM application."""

from molim.ui.cli.commands import cli
from molim.utils.config import config
from molim.utils.logging_config import logger
from molim.infrastructure.database.connection import init_database

def main():
    """Initialize and run application."""
    # Load configuration
    config.load()
    
    # Initialize database
    init_database()
    
    # Run CLI
    cli()

if __name__ == '__main__':
    main()
```

**Tasks:**
- [ ] Install click: `pip install click`
- [ ] Create CLI commands
- [ ] Implement process command
- [ ] Implement stats command
- [ ] Implement search command
- [ ] Add help text and documentation

---

## 📅 Phase 5: Tkinter GUI (Week 8-10)

### Step 5.1: Main Window Design

Create `molim/ui/gui/main_window.py`:
```python
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
from ...core.services import ProcessingService, StatisticsService
from ...core.repositories import MovieRepository

class MainWindow:
    """Main application window."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MoLiM - Movie Library Manager")
        self.root.geometry("1200x800")
        
        # Services
        self.movie_repo = None
        self.processing_service = None
        self.stats_service = None
        
        # Setup UI
        self._create_menu()
        self._create_toolbar()
        self._create_main_area()
        self._create_statusbar()
    
    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Process Folder...", 
                            command=self.process_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Statistics", 
                            command=self.show_statistics)
        view_menu.add_command(label="Reports", 
                            command=self.show_reports)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def _create_main_area(self):
        """Create main content area."""
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Movies tab
        movies_frame = ttk.Frame(self.notebook)
        self.notebook.add(movies_frame, text="Movies")
        self._create_movies_tab(movies_frame)
        
        # Statistics tab
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        self._create_statistics_tab(stats_frame)
        
        # Search tab
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Search")
        self._create_search_tab(search_frame)
    
    def _create_movies_tab(self, parent):
        """Create movies list view."""
        # Search bar
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", 
                  command=self.search_movies).pack(side=tk.LEFT)
        
        # Movies tree view
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        columns = ("Name", "Year", "Rating", "Genres", "Director", "Cast")
        self.movies_tree = ttk.Treeview(tree_frame, columns=columns, 
                                       show="headings",
                                       yscrollcommand=vsb.set,
                                       xscrollcommand=hsb.set)
        
        vsb.config(command=self.movies_tree.yview)
        hsb.config(command=self.movies_tree.xview)
        
        # Configure columns
        for col in columns:
            self.movies_tree.heading(col, text=col, 
                                   command=lambda c=col: self.sort_by(c))
            self.movies_tree.column(col, width=150)
        
        # Pack
        self.movies_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Context menu
        self.movies_tree.bind("<Button-3>", self.show_context_menu)
    
    def process_folder(self):
        """Process a folder of movies."""
        folder = filedialog.askdirectory(title="Select Folder to Process")
        if folder:
            # Show progress dialog
            ProgressDialog(self.root, folder, self.processing_service)
    
    def search_movies(self):
        """Search for movies."""
        query = self.search_entry.get()
        # Implement search
        pass

class ProgressDialog:
    """Dialog showing processing progress."""
    
    def __init__(self, parent, folder: str, processing_service):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Processing Movies")
        self.dialog.geometry("400x150")
        
        # Progress bar
        ttk.Label(self.dialog, text=f"Processing: {folder}").pack(pady=10)
        self.progress = ttk.Progressbar(self.dialog, length=300, 
                                       mode='determinate')
        self.progress.pack(pady=10)
        
        self.status_label = ttk.Label(self.dialog, text="Starting...")
        self.status_label.pack(pady=10)
        
        # Start processing in thread
        import threading
        thread = threading.Thread(target=self._process, 
                                 args=(folder, processing_service))
        thread.start()
    
    def _process(self, folder, service):
        """Process folder in background thread."""
        def update_progress(current, total):
            self.progress['value'] = (current / total) * 100
            self.status_label['text'] = f"Processed {current} of {total}"
        
        import asyncio
        asyncio.run(service.process_folder(folder, update_progress))
        
        self.dialog.destroy()
```

**Tasks:**
- [ ] Design main window layout
- [ ] Create menu bar
- [ ] Create movies list view with Treeview
- [ ] Implement search functionality
- [ ] Create progress dialog
- [ ] Add context menus

### Step 5.2: Additional GUI Components

Create other GUI components:
- `movie_details_dialog.py` - Show full movie details
- `statistics_view.py` - Charts and graphs
- `settings_dialog.py` - Application settings
- `about_dialog.py` - About application

**Tasks:**
- [ ] Create movie details dialog
- [ ] Create statistics view (consider matplotlib for charts)
- [ ] Create settings dialog
- [ ] Style with ttk themes

---

## 📅 Phase 6: Testing & Polish (Week 11-12)

### Step 6.1: Unit Tests

Create `tests/unit/test_movie_model.py`:
```python
import pytest
from molim.core.models.movie import Movie

def test_movie_creation():
    movie = Movie(name="Test Movie", year=2023, rating=7.5)
    assert movie.name == "Test Movie"
    assert movie.year == 2023
    assert movie.rating == 7.5

def test_is_directed_by():
    movie = Movie(name="Test", directors=["Christopher Nolan"])
    assert movie.is_directed_by("Christopher Nolan")
    assert movie.is_directed_by("Nolan")
    assert not movie.is_directed_by("Spielberg")

def test_rating_category():
    movie1 = Movie(rating=9.2)
    assert movie1.get_rating_category() == "masterpiece"
    
    movie2 = Movie(rating=8.5)
    assert movie2.get_rating_category() == "excellent"
```

Create tests for:
- Models
- Repositories
- Services
- Utilities

**Tasks:**
- [ ] Install pytest: `pip install pytest pytest-asyncio`
- [ ] Write unit tests for all models
- [ ] Write unit tests for repositories
- [ ] Write unit tests for services
- [ ] Achieve 80%+ code coverage

### Step 6.2: Integration Tests

Create `tests/integration/test_processing_flow.py`:
```python
import pytest
from pathlib import Path
from molim.core.services.processing_service import ProcessingService

@pytest.mark.asyncio
async def test_process_folder_integration(tmp_path):
    """Test complete folder processing flow."""
    # Setup test folder structure
    test_folder = tmp_path / "movies"
    test_folder.mkdir()
    
    movie_folder = test_folder / "The Matrix.1999.1080p"
    movie_folder.mkdir()
    
    # Process folder
    # ... test implementation
```

**Tasks:**
- [ ] Write integration tests
- [ ] Create test fixtures
- [ ] Test database operations
- [ ] Test IMDb service (with mocking)

### Step 6.3: Documentation

Create documentation:
- User guide
- API documentation (Sphinx)
- Developer guide
- Configuration guide

**Tasks:**
- [ ] Install Sphinx: `pip install sphinx`
- [ ] Generate API documentation
- [ ] Write user guide
- [ ] Add docstrings to all modules

### Step 6.4: Code Quality

**Tasks:**
- [ ] Install linters: `pip install black isort flake8 mypy`
- [ ] Format code with black
- [ ] Sort imports with isort
- [ ] Type check with mypy
- [ ] Fix all linting issues

---

## 🎯 Success Criteria

### Phase 1 Complete When:
- [x] All invalid escape sequences fixed
- [x] Configuration system implemented
- [x] Logging system implemented
- [x] New project structure created
- [x] Old code moved to legacy folder

### Phase 2 Complete When:
- [x] Database schema created
- [x] Models defined with dataclasses
- [x] Repository pattern implemented
- [x] Migration script working
- [x] All existing data migrated successfully

### Phase 3 Complete When:
- [x] IMDb service implemented with async
- [x] Processing service working
- [x] Statistics service functional
- [x] All services tested

### Phase 4 Complete When:
- [x] CLI fully functional
- [x] All commands working
- [x] Help text comprehensive
- [x] User documentation written

### Phase 5 Complete When:
- [x] Main window implemented
- [x] All tabs functional
- [x] Progress tracking working
- [x] GUI responsive and intuitive

### Phase 6 Complete When:
- [x] 80%+ test coverage
- [x] All tests passing
- [x] Documentation complete
- [x] Code quality metrics met
- [x] No critical bugs

---

## 📦 Final Deliverables

1. **Refactored Codebase**
   - Clean architecture
   - Type-safe
   - Well-documented
   - Fully tested

2. **SQLite Database**
   - Normalized schema
   - Indexed for performance
   - Migration scripts

3. **CLI Application**
   - Process folders
   - Generate statistics
   - Search movies
   - Generate reports

4. **GUI Application**
   - Intuitive interface
   - Real-time progress
   - Search and filter
   - Statistics visualization

5. **Documentation**
   - User guide
   - Developer guide
   - API documentation
   - Configuration guide

6. **Tests**
   - Unit tests
   - Integration tests
   - 80%+ coverage
   - CI/CD ready

---

## 🚀 Getting Started

1. **Read OVERVIEW.md** to understand current architecture
2. **Review this plan** and adjust based on priorities
3. **Start with Phase 1** - foundation is critical
4. **Work incrementally** - each phase builds on previous
5. **Test continuously** - don't accumulate technical debt
6. **Document as you go** - future you will thank you

---

## 💡 Tips for Success

1. **Don't skip testing** - It's tempting, but you'll regret it
2. **Keep legacy code** - Reference for business logic
3. **Commit frequently** - Small, focused commits
4. **Use branches** - Feature branches for each phase
5. **Ask for help** - GitHub Copilot is your friend
6. **Take breaks** - Refactoring is mentally demanding

---

## 🎉 Conclusion

This is an ambitious refactoring project, but the result will be a modern, maintainable, and extensible movie library management system.

The key is to work **incrementally** and **systematically**. Each phase builds on the previous, creating a solid foundation for the GUI.

**Ready to start? Begin with Phase 1, Step 1.1!**
