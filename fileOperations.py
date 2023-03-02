
from datetime import date

import os
import IMDBMovieData
import IMDBSeriesData

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

def getMovieNameFromFolder(movieFolderName): # TODO  -> tuple(str,str):
  earchMovieName = ""
  # provjeriti ima li točaka u nazivu
  parts = movieFolderName.split('.')

  # naći prvi string koji je kredibilna godina proizvodnje (1930 - 2022)
  cntParts=0
  year = 0
  searchMovieName = ""
  for part in parts:
    cntParts += 1
    # prvoga bi trebalo preskočiti (za filmove koji imaju broj u nazivu: 300, 1917, 2012)
    if cntParts == 1:
      continue
    
    if( part.isnumeric() ):
      year = int(part)
      if year > 1930 and year < 2023 :
        #nasli smo ga
        diskMovieName = ""
        searchMovieName = ""
        for piece in parts:
          if piece != part:
            diskMovieName += piece + " "
          else :
            # riješiti ukoliko ima _ na početku, da search name bude cist
            searchMovieName = diskMovieName.strip('_')

            # na diskMovieName cemo dodati i godinu
            diskMovieName += "(" + piece + ")"
            break
        
        print (diskMovieName, " - ", searchMovieName, " - ", movieFolderName)
  
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

def doesFilmDataHasMovieID(folderWhereItIs, movieFolderName, movieName, movieYear) -> bool:
  filePath = getFilmDataFilePath(folderWhereItIs, movieFolderName, movieName, movieYear)

  try:
    fileFilmData = open(filePath, 'r')
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
    fileFilmData = open(filePath, 'r')
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
    newDirName = getMovieFolderNameFromMovieData(series_data)   # movie_data.name + "(" + str(movie_data.year) + ")" + " IMDB-" + str(movie_data.rating) + " " + movie_data.genres + " CAST - " + movie_data.cast

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
      #os.rename(origDir, destDir)

    print()

def saveTXTWithMovieData(movie_data : IMDBMovieData, folderWhereItIs, movieFolderName):
  # formirati TXT datoteku s podacima
  fileName = getFilmDataFilePath(folderWhereItIs, movieFolderName, movie_data.name, movie_data.year)

  fileFilmData = open(fileName, 'w')
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
  fileName = getFilmDataFilePath(folderWhereItIs, movieFolderName, series_data.name, series_data.year)

  fileFilmData = open(fileName, 'w')
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
    fileName = folderWhereItIs + "\\" + movieFolderName + "\\Season " + str(season.seasonID)
    fileFilmData = open(fileName, 'w')
    fileFilmData.write("SeasonID:    " + str(season.seasonID) + "\n")
    fileFilmData.write("Num episodes:" + str(season.num_episodes) + "\n")
    fileFilmData.close()
 
def loadIMDBMovieDataFromFilmData(folderWhereItIs, movieFolderName, movieName, movieYear) -> IMDBMovieData.IMDBMovieData:
  movie_data = IMDBMovieData.IMDBMovieData(movieName)

  filePath = getFilmDataFilePath(folderWhereItIs, movieFolderName, movieName, movieYear)

  try:
    fileFilmData = open(filePath, 'r')
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
