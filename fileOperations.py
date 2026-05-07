from datetime import date

import os
import re
import shutil
import IMDBMovieData
import IMDBSeriesData

# Video file extensions recognised when promoting loose files into folders.
# Lowercase, leading dot. Compared case-insensitively.
VIDEO_EXTENSIONS = {
    ".mkv", ".mp4", ".avi", ".mov", ".wmv", ".m4v",
    ".ts", ".m2ts", ".webm", ".mpg", ".mpeg", ".flv",
}


def promoteLooseVideoFilesToFolders(folderName: str) -> int:
  """Move loose video files at the top of *folderName* into per-movie folders.

  For every video file directly under *folderName*, create a sibling folder
  named after the file's stem and move the file (plus any same-stem sidecar
  files such as .srt subtitles) into it. Files already inside a subfolder
  are not touched. Returns the number of files promoted.

  Idempotent: running it again on the same folder is a no-op because the
  files are no longer loose.
  """
  if not os.path.isdir(folderName):
    return 0

  promoted = 0
  for entry in list(os.scandir(folderName)):
    if not entry.is_file():
      continue
    stem, ext = os.path.splitext(entry.name)
    if ext.lower() not in VIDEO_EXTENSIONS:
      continue
    if not stem.strip():
      continue

    targetDir = os.path.join(folderName, stem)
    # If a folder with the exact stem already exists, reuse it; otherwise
    # create it. os.makedirs(exist_ok=True) covers the rare race.
    os.makedirs(targetDir, exist_ok=True)

    # Move the video file.
    destVideo = os.path.join(targetDir, entry.name)
    if os.path.exists(destVideo):
      print(f"  SKIP: {destVideo} already exists")
      continue
    print(f"  PROMOTING: {entry.name} -> {stem}/")
    shutil.move(entry.path, destVideo)
    promoted += 1

    # Sweep along sidecar files that share the stem (subtitles, nfo, etc.).
    for sidecar in list(os.scandir(folderName)):
      if not sidecar.is_file():
        continue
      side_stem, _ = os.path.splitext(sidecar.name)
      if side_stem == stem:
        destSide = os.path.join(targetDir, sidecar.name)
        if not os.path.exists(destSide):
          print(f"    + sidecar: {sidecar.name}")
          shutil.move(sidecar.path, destSide)

  return promoted


def getFolderSize(start_path : str):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def getNameYearFromNameWithIMDB(movieFolderName : str) :
  ind1 = movieFolderName.find("(")
  ind2 = movieFolderName.find(")")

  imdb_name_raw = movieFolderName[0:ind1-1]
  if imdb_name_raw.startswith("zzz"):
    imdb_name1 = movieFolderName[4:ind1-1]
  else:
    imdb_name1 = imdb_name_raw

  imdb_name = imdb_name1.strip("_") 
  year_str  = movieFolderName[ind1+1:ind2]

  return (imdb_name, year_str)


def getFilmDataFilePath(folderWhereItIs : str, movieFolderName : str, movieName : str, movieYear : int) -> str:
  beba = movieName.strip()
  filePath = folderWhereItIs + "\\" + movieFolderName + "\\" + "Film data - " + movieName.strip() + " (" + str(movieYear) + ")" + ".txt"
  return filePath

def getSeriesDataFilePath(folderWhereItIs : str, movieFolderName : str, movieName : str, movieYear : int) -> str:
  beba = movieName.strip()
  filePath = folderWhereItIs + "\\" + movieFolderName + "\\" + "Series data - " + movieName.strip() + " (" + str(movieYear) + ")" + ".txt"
  return filePath

def getMovieNameFromFolder(movieFolderName): # TODO  -> tuple(str,str):
  """Extract (title, year) from a release-style folder name.

  Recognises any of '.', '-', '_' or whitespace as a separator. The first
  4-digit token in 1931..(currentYear+1), at any position other than the
  very first (so titles like '300', '1917', '2012' aren't mis-detected as
  years), is treated as the production year. The title is everything
  before that token, joined with single spaces and stripped of leading
  underscores.

  When no year is present, also looks for a season marker token
  (``S01``, ``S1E02``, ``Season 1`` ...) anywhere after the first token
  and treats it as an end-of-title marker. In that case ``year`` is
  returned as ``0`` (unknown) but the title is still extracted, so
  one-season scene releases like
  ``Copenhagen.Cowboy.S01.COMPLETE.720p.NF.WEBRip.x264-GalaxyTV[TGx]``
  resolve to ``("Copenhagen Cowboy", 0)``.

  Returns ('', 0) when neither a plausible year nor a season marker is
  found.
  """
  parts = re.split(r'[.\-_\s\(\)\[\]\{\}]+', movieFolderName)
  parts = [p.strip("()[]{}") for p in parts if p]

  max_year = date.today().year + 1
  season_re = re.compile(r'^[Ss]\d{1,2}([Ee]\d{1,2})?$')

  title_pieces = []
  year = 0
  stop_on_season = False
  for idx, part in enumerate(parts):
    # Skip the very first token so that titles like '300', '1917', '2012'
    # aren't mistaken for years, and a leading 'S01' doesn't kill the title.
    if idx > 0:
      if len(part) == 4 and part.isdigit():
        candidate = int(part)
        if 1930 < candidate <= max_year:
          year = candidate
          break
      # Season markers: S01, S1, S01E02, or the literal word 'Season'
      # (optionally followed by a number token).
      if season_re.match(part) or part.lower() == "season":
        stop_on_season = True
        break
    title_pieces.append(part)

  if year == 0 and not stop_on_season:
    return ("", 0)

  searchMovieName = " ".join(p for p in title_pieces if p).strip().lstrip("_").strip()
  if year:
    diskMovieName = searchMovieName + " (" + str(year) + ")"
    print(diskMovieName, " - ", searchMovieName, " - ", movieFolderName)
  else:
    print(searchMovieName, " - (no year, season marker)", " - ", movieFolderName)

  return (searchMovieName, year)

def getYearFromIMDBFolderName(movieFolderName : str) -> int :
  ind1 = movieFolderName.find("(")
  ind2 = movieFolderName.find(")")
  year_str  = movieFolderName[ind1+1:ind2]
  
  return int(year_str)

def getRatingFromIMDBFolderName(movieFolderName : str) -> float :
  ind = movieFolderName.find("IMDB-")
  rating = movieFolderName[ind+5:ind+8]
  return float(rating)

def getMovieFolderNameFromMovieData(movie_data : IMDBMovieData) -> str:
  prefix = ""
  if movie_data.rating >= 9.0:
    prefix = "___"
  elif movie_data.rating >= 8.0:
    prefix = "__"
  elif movie_data.rating >= 7.0:
    prefix = "_"
  elif movie_data.rating < 6.0:
    prefix = "zzz_"
  
  newDirName = prefix + str(movie_data.name).rstrip() + "  (" + str(movie_data.year) + ")" + " IMDB-" + str(movie_data.rating) + " " + movie_data.genres + " CAST - " + movie_data.cast_leads
  
  return newDirName

def getSeriesFolderNameFromMovieData(series_data : IMDBSeriesData) -> str:
  prefix = ""
  if series_data.rating >= 9.0:
    prefix = "___"
  elif series_data.rating >= 8.0:
    prefix = "__"
  elif series_data.rating >= 7.0:
    prefix = "_"
  elif series_data.rating < 6.0:
    prefix = "zzz_"
  
  newDirName = prefix + str(series_data.name).rstrip() + "  (" + str(series_data.year) + ", " + str(series_data.num_seasons) + " seasons)" + " IMDB-" + str(series_data.rating) + " " + series_data.genres + " CAST - " + series_data.cast_leads
  
  return newDirName

def doesFilmDataHasMovieID(folderWhereItIs, movieFolderName, movieName, movieYear) -> bool:
  filePath = getFilmDataFilePath(folderWhereItIs, movieFolderName, movieName, movieYear)

  try:
    fileFilmData = open(filePath, 'r', encoding='utf-8')
  except:
    return False

  if fileFilmData:
    first = fileFilmData.readline()
    second = fileFilmData.readline()
    
    if second.startswith("MovieID:"):
      return True

  return False

def getMovieIDFromFilmData(folderWhereItIs, movieFolderName, movieName, movieYear) :
  filePath = getFilmDataFilePath(folderWhereItIs, movieFolderName, movieName, movieYear)

  try:
    fileFilmData = open(filePath, 'r', encoding='utf-8')
  except:
    return None

  if fileFilmData:
    fileFilmData.readline()             # skipping first line
    second = fileFilmData.readline()
    
    if second.startswith("MovieID:"):
      movieID = second[10:].strip()
      return movieID

  return None

def saveMovieDataAndRenameFolder(movie_data : IMDBMovieData, folderWhereItIs, movieFolderName):

    # ime novog direktorija
    # Naziv (2022) IMDB-7.5 Adventure,Comedy,Thriller Cast-Mel Gibson, Jim Belushi, Joan Crawford
    newDirName = getMovieFolderNameFromMovieData(movie_data)   # movie_data.name + "(" + str(movie_data.year) + ")" + " IMDB-" + str(movie_data.rating) + " " + movie_data.genres + " CAST - " + movie_data.cast

    print("NEWDIR = ", newDirName)

    # formirati TXT datoteku s podacima
    saveTXTWithMovieData(movie_data, folderWhereItIs, movieFolderName)

    # i sad idemo preimenovati direktorij
    origDir = folderWhereItIs + "\\" + movieFolderName
    destDir = folderWhereItIs + "\\" + newDirName

    if os.path.isdir(destDir):
      print("\n\nDESTINATION DIR ALREADY EXISTS!!!!!!\n\n")
    else:
      print("RENAMING - ", origDir, destDir)
      os.rename(origDir, destDir)

    print()


def saveSeriesDataAndRenameFolder(series_data : IMDBSeriesData, folderWhereItIs, movieFolderName):

    # ime novog direktorija
    # Naziv (2022) IMDB-7.5 Adventure,Comedy,Thriller Cast-Mel Gibson, Jim Belushi, Joan Crawford
    newDirName = getSeriesFolderNameFromMovieData(series_data)   # movie_data.name + "(" + str(movie_data.year) + ")" + " IMDB-" + str(movie_data.rating) + " " + movie_data.genres + " CAST - " + movie_data.cast

    print("NEWDIR = ", newDirName)

    # formirati TXT datoteku s podacima
    saveTXTWithSeriesData(series_data, folderWhereItIs, movieFolderName)

    # i sad idemo preimenovati direktorij
    origDir = folderWhereItIs + "\\" + movieFolderName
    destDir = folderWhereItIs + "\\" + newDirName

    if os.path.isdir(destDir):
      print("\n\nDESTINATION DIR ALREADY EXISTS!!!!!!\n\n")
    else:
      print("RENAMING - ", origDir, destDir)
      os.rename(origDir, destDir)

    print()

def saveTXTWithMovieData(movie_data : IMDBMovieData, folderWhereItIs, movieFolderName):
  # formirati TXT datoteku s podacima
  fileName = getFilmDataFilePath(folderWhereItIs, movieFolderName, movie_data.name, movie_data.year)

  fileFilmData = open(fileName, 'w', encoding='utf-8')
  fileFilmData.write(movie_data.name + " (" + str(movie_data.year) + ")\n")
  fileFilmData.write("MovieID:   " + str(movie_data.movieID) + "\n")
  fileFilmData.write("Title:     " + movie_data.imdb_name + "\n")
  fileFilmData.write("Year:      " + str(movie_data.year) + "\n")
  fileFilmData.write("Released:  " + movie_data.releaseDate + "\n")
  fileFilmData.write("Runtime:   " + str(movie_data.runtime) + " min\n")
  fileFilmData.write("Rating:    " + str(movie_data.rating) + "\n")
  if movie_data.top250rank != 0 :
    fileFilmData.write("Top 250:   " + str(movie_data.top250rank) + "\n")
  fileFilmData.write("Votes:     " + str(movie_data.votes) + "\n")
  fileFilmData.write("Genres:    " + movie_data.genres + "\n")
  fileFilmData.write("Directors: " + movie_data.directors + "\n")
  fileFilmData.write("Countries: " + movie_data.countries + "\n")
  fileFilmData.write("Languages: " + movie_data.languages + "\n")
  fileFilmData.write("Producers: " + movie_data.producers + "\n")
  fileFilmData.write("Writers:   " + movie_data.writers + "\n")
  fileFilmData.write("Box office:" + movie_data.box_office + "\n")
  fileFilmData.write("Cast:      " + movie_data.cast_complete + "\n")
  fileFilmData.write("Plot:      " + str(movie_data.plot) + "\n")

  today = date.today()
  dateToSave = today.strftime("%Y-%m-%d")
  fileFilmData.write("Saved on:  " + dateToSave)

  fileFilmData.close()
 

def saveTXTWithSeriesData(series_data : IMDBSeriesData, folderWhereItIs, movieFolderName):
  # formirati TXT datoteku s podacima
  fileName = getSeriesDataFilePath(folderWhereItIs, movieFolderName, series_data.name, series_data.year)

  fileFilmData = open(fileName, 'w', encoding='utf-8')
  fileFilmData.write(series_data.name + " (" + str(series_data.year) + ")\n")
  fileFilmData.write("MovieID:   " + str(series_data.movieID) + "\n")
  fileFilmData.write("Title:     " + series_data.imdb_name + "\n")
  fileFilmData.write("Year:      " + str(series_data.year) + "\n")
  fileFilmData.write("Runtime:   " + str(series_data.runtime) + " min\n")
  fileFilmData.write("Rating:    " + str(series_data.rating) + "\n")
  fileFilmData.write("Votes:     " + str(series_data.votes) + "\n")
  fileFilmData.write("Genres:    " + series_data.genres + "\n")
  fileFilmData.write("Countries: " + series_data.countries + "\n")
  fileFilmData.write("Languages: " + series_data.languages + "\n")
  fileFilmData.write("Writers:   " + series_data.writers + "\n")
  fileFilmData.write("Cast:      " + series_data.cast_complete + "\n")
  fileFilmData.write("Plot:      " + str(series_data.plot) + "\n")

  today = date.today()
  dateToSave = today.strftime("%Y-%m-%d")
  fileFilmData.write("Saved on:  " + dateToSave)

  fileFilmData.close()

  for season in series_data.seasons_list:
    fileName = folderWhereItIs + "\\" + movieFolderName + "\\Season " + str(season.seasonID) + ".txt"
    fileFilmData = open(fileName, 'w', encoding='utf-8')
    fileFilmData.write("SeasonID:    " + str(season.seasonID) + "\n")
    fileFilmData.write("Num episodes:" + str(season.num_episodes) + "\n")

    for episode in season.episodes_list:
      fileFilmData.write("\nEpisode   : " + str(episode.title) + "\n")
      fileFilmData.write("Rating    : " + str(episode.rating) + "\n")
      fileFilmData.write("Votes     : " + str(episode.votes) + "\n")
      fileFilmData.write("Air date  : " + str(episode.original_air_date) + "\n")
      fileFilmData.write("Year      : " + str(episode.year) + "\n")
      fileFilmData.write("Plot      : " + episode.plot + "\n")

    fileFilmData.close()

 
def loadIMDBMovieDataFromFilmData(folderWhereItIs, movieFolderName, movieName, movieYear) -> IMDBMovieData.IMDBMovieData:
  movie_data = IMDBMovieData.IMDBMovieData(movieName)

  filePath = getFilmDataFilePath(folderWhereItIs, movieFolderName, movieName, movieYear)

  try:
    fileFilmData = open(filePath, 'r', encoding='utf-8')
  except:
    movie_data.name = ""
    return movie_data

  name_and_year = fileFilmData.readline()
  lines = fileFilmData.readlines()
  for line in lines:
    if line.startswith("Title:"):
      title = line[10:].strip()
      movie_data.imdb_name = title
    elif line.startswith("MovieID:"):
      movieID = line[10:].strip()
      movie_data.movieID = movieID
    elif line.startswith("Year:"):
      year_str = line[10:].strip()
      movie_data.year = int(year_str)
    elif line.startswith("Runtime:"):
      ind = line.find("min")
      runtime = line[10:ind-1].strip()
      movie_data.runtime = runtime
    elif line.startswith("Released:"):
      release_date = line[10:].strip()
      movie_data.releaseDate = release_date
    elif line.startswith("Rating:"):
      rating = line[10:].strip()
      movie_data.rating = float(rating)
    elif line.startswith("Top 250:"):
      top250rank  = line[10:].strip()
      movie_data.top250rank = int(top250rank)
    elif line.startswith("Genres:"):
      genres = line[10:].strip()
      movie_data.genres = genres
    elif line.startswith("Directors:"):
      directors = line[10:].strip()
      movie_data.directors = directors
    elif line.startswith("Countries:"):
      countries = line[10:].strip()
      movie_data.countries = countries
    elif line.startswith("Languages:"):
      languages = line[10:].strip()
      movie_data.languages = languages
    elif line.startswith("Producers:"):
      producers = line[10:].strip()
      movie_data.producers = producers
    elif line.startswith("Writers:"):
      writers = line[10:].strip()
      movie_data.writers = writers
    elif line.startswith("Cast:"):
      cast = line[10:].strip()
      movie_data.cast_complete = cast
      # TODO - formirati i cast_lead
    elif line.startswith("Plot:"):
      plot = line[10:].strip()
      movie_data.plot = plot
    
  if movie_data.rating == 0.0:
    movie_data.rating = getRatingFromIMDBFolderName(movieFolderName)

  if movie_data.year == 0:
    movie_data.year = getYearFromIMDBFolderName(movieFolderName)

  return movie_data
