# MoLiM - Movie Library Manager
## Project Overview & Deep Dive Analysis

---

## 📋 Table of Contents
1. [Purpose & Functionality](#purpose--functionality)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Data Model](#data-model)
5. [Key Features](#key-features)
6. [Current Issues & Technical Debt](#current-issues--technical-debt)
7. [Opportunities for Improvement](#opportunities-for-improvement)

---

## 🎯 Purpose & Functionality

**MoLiM** is a sophisticated movie library management system designed to:
- **Organize** a physical movie collection stored in folders on disk
- **Fetch** and **cache** movie metadata from IMDb
- **Generate** statistics and reports about your movie collection
- **Categorize** movies by directors, actors, genres, and decades
- **Track** TV series with season and episode details

### Folder Organization Strategy
The system uses a clever **underscore prefix system** to indicate IMDb ratings:
- `___` (3 underscores) = Rating ≥ 9.0 (Masterpieces)
- `__` (2 underscores) = Rating ≥ 8.0 (Excellent)
- `_` (1 underscore) = Rating ≥ 7.0 (Good)
- `zzz_` = Rating < 6.0 (Poor quality)

**Folder naming convention:**
```
_Movie Name (2023) IMDB-7.5 Action,Thriller CAST - Actor1, Actor2
```

---

## 🏗️ Architecture Overview

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        MoLiM.py                             │
│                   (Main Entry Point)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Processing  │ │  Statistics  │ │   Reports    │
│   Module     │ │    Module    │ │    Module    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ RootFolder   │ │  IMDBAccess  │ │FileOperations│
│   (Data      │ │  (API Layer) │ │ (Persistence)│
│  Aggregator) │ └──────────────┘ └──────────────┘
└──────┬───────┘
       │
       ▼
┌──────────────┐
│FolderWith    │
│   Movies     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ IMDBMovie    │
│    Data      │
│  (Model)     │
└──────────────┘
```

### Data Flow
```
1. User → Processes folder of movies
2. Processing → Extracts movie names from folder structure
3. IMDBAccess → Fetches data from IMDb API (Cinemagoer)
4. FileOperations → Saves data as text files
5. FileOperations → Renames folders with IMDb metadata
6. RootFolder → Loads cached data for analysis
7. Statistics/Reports → Generates insights
```

---

## 🔧 Core Components

### 1. **MoLiM.py** - Main Application
- **Purpose**: Entry point and orchestration
- **Functions**:
  - `printDirectorsStatistics()` - Top 10 movies per director
  - `printActorsStatistics()` - Top 10 movies per actor
  - `printAllActorsMovies()` - Complete filmography per actor
- **Current Mode**: Primarily used as a script runner with commented-out function calls

### 2. **processing.py** - Data Processing Pipeline
- **Purpose**: Coordinates the IMDb data fetching workflow
- **Key Functions**:
  - `processFolder(folderName)` - Process all movies in a folder
  - `processSeriesFolder(folderName)` - Process TV series
  - `folderRecheckDataWithIMDB()` - Update existing data
  - `reprocessFolderIMDBData()` - Re-fetch IMDb data using cached IDs
- **Workflow**:
  1. Scan folder for movie directories
  2. Extract movie name and year from folder name
  3. Fetch IMDb data
  4. Save data to text file
  5. Rename folder with metadata

### 3. **imdbAccess.py** - IMDb API Layer
- **Purpose**: Interface with IMDb via Cinemagoer library
- **Key Functions**:
  - `fetchMovieData(searchMovieName, releaseYear)` - Search and fetch
  - `fetchMovieDataByMovieID(name, movieID)` - Direct fetch by ID
  - `fetchSeriesData(searchSeriesName)` - TV series data
  - `fetchSeriesDataByMovieID(name, movieID)` - Series by ID
- **Features**:
  - Rate limiting (5-10 second delays)
  - Error handling for network issues
  - Comprehensive metadata extraction (cast, crew, ratings, etc.)

### 4. **fileOperations.py** - File I/O & Persistence
- **Purpose**: All file system operations
- **Key Functions**:
  - `getMovieNameFromFolder()` - Parse folder names
  - `getMovieFolderNameFromMovieData()` - Generate new folder names
  - `saveTXTWithMovieData()` - Persist metadata to text file
  - `loadIMDBMovieDataFromFilmData()` - Load cached metadata
  - `doesFilmDataHasMovieID()` - Check if data is complete
  - `getFolderSize()` - Calculate directory size
- **File Format**: Plain text "Film data - [Movie Name] ([Year]).txt"

### 5. **Data Models**
#### **IMDBMovieData.py**
```python
class IMDBMovieData:
    - name, imdb_name, movieID
    - year, runtime, rating, votes
    - directors, producers, writers
    - genres, countries, languages
    - cast_leads, cast_complete, plot
    - box_office, top250rank, releaseDate
    
    Methods:
    - isDirectedBy(director) → bool
    - hasGenre(genre) → bool
    - hasActor(actor) → bool
```

#### **IMDBSeriesData.py**
```python
class IMDBSeriesData:
    - Similar to IMDBMovieData
    - num_seasons
    - seasons_list (IMDBSeriesSeasonData)
```

#### **IMDBSeriesSeasonData.py** & **IMDBEpisodeData.py**
- Season and episode level details for TV series

### 6. **RootFolder.py** & **FolderWithMovies.py** - Data Aggregation
- **Purpose**: Load and query movie collections
- **RootFolder**: Aggregates multiple folders, handles deduplication
- **FolderWithMovies**: Represents a single category folder
- **Query Methods**:
  - `getMoviesWithRatingHigherThan(rating)`
  - `getMoviesWithRatingHigherThanWithGivenDirector(rating, director)`
  - `getMoviesWithRatingHigherThanWithGivenGenre(rating, genre)`
  - `getMoviesWithRatingHigherThanWithGivenActor(rating, actor)`

### 7. **movieStatistics.py** - Statistical Analysis
- **Purpose**: Generate collection statistics
- **Functions**:
  - `folderStatistics()` - Breakdown by rating ranges
  - `folderSizeStatistic()` - Disk space analysis
  - `printDecadesStatistics()` - Movies per decade
  - `printBigFiles()` - Find large files (> 1GB)

### 8. **reports.py** - Report Generation
- **Purpose**: Identify missing data
- **Functions**:
  - `rootFolderReportNotDone()` - Movies without IMDb data
  - `rootFolderReportNoIMDBData()` - Incomplete metadata

### 9. **myFolders.py** - Configuration
- **Purpose**: Hardcoded folder paths and lists
- **Contains**:
  - `directorsFolders` - Paths to director collections
  - `actorsFolders` - Paths to actor collections
  - `genresFolders` - Genre category paths
  - `decadesFolders` - Decade category paths
  - `directorsList`, `actorsList` - Names for filtering

### 10. **testTkinter.py** - UI Experiment
- Basic Tkinter widgets (Labels, Listbox, Treeview)
- Not integrated with the main application

---

## 📊 Data Model

### Storage Strategy: **Hybrid (File System + Text Files)**

```
Z:\Movies\FILMOVI\
├── __Alfred Hitchcock/
│   ├── __Psycho (1960) IMDB-8.5 Horror,Mystery CAST - Anthony Perkins.../
│   │   ├── Film data - Psycho (1960).txt
│   │   └── Psycho.1960.1080p.BluRay.mkv
│   └── __Rear Window (1954) IMDB-8.5 Mystery,Thriller CAST - James Stewart.../
├── ___Al Pacino/
├── ____Action, Crime & Thriller/
├── _1970's/
└── _Breaking Bad (2008, 5 seasons) IMDB-9.5.../
    ├── Series data - Breaking Bad (2008).txt
    ├── Season 1.txt
    ├── Season 2.txt
    └── ...
```

### Text File Format (Film data - Movie Name (Year).txt)
```
Movie Name (2023)
MovieID:   1234567
Title:     Official IMDB Title
Year:      2023
Released:  2023-05-15
Runtime:   142 min
Rating:    7.8
Top 250:   145
Votes:     285000
Genres:    Action, Thriller, Crime
Directors: Director Name
Countries: ['USA', 'UK']
Languages: ['English']
Producers: Producer1, Producer2
Writers:   Writer1, Writer2
Box office:{'Budget': '$150,000,000', 'Cumulative Worldwide Gross': '$850,000,000'}
Cast:      Actor1, Actor2, Actor3, ...
Plot:      Movie plot summary
Saved on:  2024-11-28
```

---

## 🎪 Key Features

### ✅ What Works Well
1. **Comprehensive Metadata**: Rich IMDb data extraction
2. **Folder Organization**: Smart naming convention with ratings
3. **Deduplication**: Movies appearing in multiple categories handled correctly
4. **Rate Limiting**: Respects IMDb API with delays
5. **Error Handling**: Network failures handled gracefully
6. **Flexible Querying**: Filter by director, actor, genre, rating
7. **Series Support**: TV series with season/episode tracking
8. **Statistics**: Useful insights into collection

### 🎯 Use Cases
1. **Initial Processing**: Process new movie downloads
2. **Data Updates**: Refresh IMDb metadata periodically
3. **Discovery**: Find top movies by favorite directors/actors
4. **Reporting**: Identify missing or incomplete data
5. **Organization**: Maintain consistent folder structure

---

## ⚠️ Current Issues & Technical Debt

### 1. **Architecture Issues**
- **No Separation of Concerns**: Business logic mixed with I/O
- **Hardcoded Paths**: All paths in `myFolders.py` are absolute and system-specific
- **Global State**: IMDb API instance (`ia`) is global
- **Procedural Style**: Lacks proper OOP design patterns
- **No Database**: Relying on text files is fragile and slow

### 2. **Code Quality Issues**
- **No Error Handling**: Many functions can crash without graceful degradation
- **Magic Numbers**: Ratings thresholds (6.0, 7.0, 8.0, 9.0) scattered throughout
- **Code Duplication**: Similar logic repeated across functions
- **Poor Naming**: Variable names like `beba`, `ind1`, `ind2`
- **No Type Hints**: Missing type annotations (except a few)
- **No Docstrings**: Functions lack documentation
- **Commented Code**: Lots of dead code in `MoLiM.py`

### 3. **Data Issues**
- **String Parsing**: Fragile folder name parsing logic
- **Invalid Escapes**: String literals with unescaped backslashes (warnings)
- **No Validation**: No checks for data integrity
- **Encoding Issues**: Potential problems with special characters
- **No Versioning**: Text file format has no version marker

### 4. **Performance Issues**
- **Slow Queries**: Loading all movies to filter is inefficient
- **No Caching**: RootFolder loads everything each time
- **Sequential Processing**: No parallel processing of folders
- **File I/O**: Reading text files repeatedly

### 5. **Scalability Issues**
- **In-Memory Processing**: All data loaded into memory
- **No Pagination**: Can't handle very large collections
- **No Indexing**: Linear search through all movies

### 6. **Maintenance Issues**
- **No Tests**: Zero unit tests
- **No Configuration**: All settings hardcoded
- **No Logging**: Only print statements
- **Platform Specific**: Windows path separators (`\\`)
- **No CLI**: Functions called via commented code

### 7. **Security Issues**
- **No Input Validation**: Folder names could cause path traversal
- **Unsafe File Operations**: No checks before rename/delete

---

## 🚀 Opportunities for Improvement

### Immediate Wins (Low Effort, High Impact)
1. **Fix String Escapes**: Use raw strings or proper escapes
2. **Add Configuration File**: YAML/JSON for paths and settings
3. **Proper CLI**: Use `argparse` or `click`
4. **Logging**: Replace print with proper logging
5. **Constants Module**: Extract magic numbers and strings

### Short-Term Improvements (Medium Effort)
1. **Database Migration**: SQLite for metadata storage
2. **Repository Pattern**: Separate data access from business logic
3. **Service Layer**: Dedicated services for IMDb, processing, reports
4. **Error Handling**: Try-except blocks with meaningful errors
5. **Type Hints**: Full type annotations
6. **Documentation**: Docstrings for all functions/classes

### Long-Term Refactoring (High Effort, High Value)
1. **MVC Architecture**: Model-View-Controller separation
2. **Async Processing**: Use asyncio for IMDb fetching
3. **Cache Layer**: Redis or in-memory cache for queries
4. **REST API**: FastAPI backend for programmatic access
5. **Modern UI**: Tkinter or web-based UI (React/Flask)
6. **Testing Suite**: Unit tests, integration tests, fixtures
7. **Plugin System**: Extensible for different data sources

### GUI Preparation (For Tkinter Integration)
1. **Command Pattern**: Encapsulate operations as commands
2. **Observer Pattern**: Notify UI of processing progress
3. **ViewModel Layer**: Present data in UI-friendly format
4. **Threading**: Keep UI responsive during long operations
5. **State Management**: Track application state properly

---

## 📐 Recommended New Architecture (For Refactoring)

```
molim/
├── core/
│   ├── models/          # Data models (Movie, Series, Person)
│   ├── repositories/    # Data access layer (DB, File)
│   └── services/        # Business logic (IMDBService, ProcessingService)
├── infrastructure/
│   ├── database/        # SQLite schema and migrations
│   ├── cache/           # Caching layer
│   └── imdb/           # IMDb API client
├── ui/
│   ├── cli/            # Command-line interface
│   └── gui/            # Tkinter GUI
├── utils/
│   ├── config.py       # Configuration management
│   ├── logging.py      # Logging setup
│   └── validators.py   # Input validation
├── tests/              # Test suite
├── config.yaml         # Configuration file
└── main.py            # Application entry point
```

---

## 🎨 Design Patterns to Apply

1. **Repository Pattern**: Abstract data storage (files → database)
2. **Factory Pattern**: Create IMDbMovieData, IMDbSeriesData objects
3. **Strategy Pattern**: Different processing strategies (movies vs series)
4. **Observer Pattern**: Notify UI of progress updates
5. **Singleton Pattern**: Configuration, database connection
6. **Command Pattern**: Encapsulate operations for undo/redo
7. **Facade Pattern**: Simplify complex subsystems

---

## 💡 Key Recommendations

### Priority 1: Stability
- Fix invalid escape sequences
- Add comprehensive error handling
- Create configuration file for paths
- Add logging infrastructure

### Priority 2: Maintainability
- Migrate to SQLite database
- Implement repository pattern
- Add type hints and docstrings
- Create service layer

### Priority 3: Features
- Build proper CLI with argparse
- Create Tkinter GUI
- Add search functionality
- Support for movie collections/lists

### Priority 4: Quality
- Write unit tests
- Add integration tests
- Set up CI/CD
- Code formatting (black, isort)

---

## 📈 Success Metrics

After refactoring, the system should have:
- ✅ **95%+ test coverage**
- ✅ **< 1 second** query response time for typical searches
- ✅ **Zero hardcoded paths** (all in config)
- ✅ **Complete type hints** (passes mypy strict)
- ✅ **Full logging** (DEBUG, INFO, WARNING, ERROR levels)
- ✅ **Async processing** (non-blocking UI)
- ✅ **SQLite backend** (structured data storage)
- ✅ **Cross-platform** (Windows, Linux, Mac)

---

## 🎯 Conclusion

MoLiM is a **functional but monolithic** system that successfully manages a movie library with IMDb integration. It has a solid foundation but needs architectural improvements for scalability, maintainability, and GUI integration.

The code shows evidence of organic growth over time - it works, but it's time to refactor with modern Python practices, proper architecture, and a user-friendly interface.

**Next Steps**: See `REFACTORING_PLAN.md` for detailed refactoring roadmap.
