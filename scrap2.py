﻿from re import search
from sys import orig_argv
from typing import Tuple
from xmlrpc.client import Boolean
from imdb import Cinemagoer

import time
import random
import os

 
otherActorsFolder = "Z:\Movies\FILMOVI\__00_Actors_others"
otherDirectorsFolder = "Z:\Movies\FILMOVI\__00_Directors_others"

directorsFolders = [ "Z:\Movies\FILMOVI\__Akira Kurosawa",       \
  "Z:\Movies\FILMOVI\__Alfred Hitchcock",       \
  "Z:\Movies\FILMOVI\__Christopher Nolan",      \
  "Z:\Movies\FILMOVI\__Coen brothers",          \
  "Z:\Movies\FILMOVI\__John Ford",              \
  "Z:\Movies\FILMOVI\__Martic Scorsese",        \
  "Z:\Movies\FILMOVI\__Quentin Tarantino",      \
  "Z:\Movies\FILMOVI\__Ridley Scott",           \
  "Z:\Movies\FILMOVI\__Stanley Kubrick",        \
  "Z:\Movies\FILMOVI\__Steven Spielberg"
]  

directorsList = [ "Akira Kurosawa",     \
                  "Alfred Hitchcock",   \
                  "Christopher Nolan",  \
                  "Coen brothers",      \
                  "John Ford"           \
                  "Martin Scorsese",    \
                  "Quentin Tarantino"   \
                  "Ridley Scott",       \
                  "Stanley Kubrick",    \
                  "Steven Spielberg" ]

actorsFolders = [ "Z:\Movies\FILMOVI\___Al Pacino",   \
  "Z:\Movies\FILMOVI\___Bruce Lee",                   \
  "Z:\Movies\FILMOVI\___Clint Eastwood",              \
  "Z:\Movies\FILMOVI\___Daniel Day Lewis",            \
  "Z:\Movies\FILMOVI\___Jack Nicholson",              \
  "Z:\Movies\FILMOVI\___John Wayne",                  \
  "Z:\Movies\FILMOVI\___Mel Gibson",                  \
  "Z:\Movies\FILMOVI\___Robert De Niro",              \
  "Z:\Movies\FILMOVI\___Tom Cruise",                  \
  "Z:\Movies\FILMOVI\___Tom Hanks",
]  

genresFolders = [ "Z:\Movies\FILMOVI\____Action, Crime & Thriller",       \
  "Z:\Movies\FILMOVI\____Biography & History",       \
  "Z:\Movies\FILMOVI\____Comedy",       \
  "Z:\Movies\FILMOVI\____Drama",       \
  "Z:\Movies\FILMOVI\____Europe & Asia movies",       \
  "Z:\Movies\FILMOVI\____Horrors",       \
  "Z:\Movies\FILMOVI\____Science Fiction & Fantasy",       \
  "Z:\Movies\FILMOVI\____War movies",       \
  "Z:\Movies\FILMOVI\____Westerns"
]  

decadesFolders = [ "Z:\Movies\FILMOVI\_1930-60",       \
  "Z:\Movies\FILMOVI\_1970's",       \
  "Z:\Movies\FILMOVI\_1980's",       \
  "Z:\Movies\FILMOVI\_1990's",       \
  "Z:\Movies\FILMOVI\_2000's",       \
  "Z:\Movies\FILMOVI\_2010's",       \
  "Z:\Movies\FILMOVI\_2020's"
]  

class IMDBMovieData(object):
  def __init__(self,name):        # poziva se kod inicijalizacije
    self.name = name
    self.imdb_name = ""
    self.movieID = 0
    self.year = 0
    self.runtime = 0
    self.rating = 0.0
    self.votes = 0
    self.directors = ""
    self.producers = ""
    self.writers = ""
    self.genres = ""
    self.cast = ""
    self.cast_complete = ""
    self.plot = ""
    
    self.box_office = ""
    
    self.directors_list = []
    self.genres_list = []
    self.short_cast = ""
    self.cast_list = []
    self.producers_list = []
    self.writers_list = []

  def isDirectedBy(self, director : str) -> bool:
    if self.directors.find(director) != -1:
      return True
    else:
      return False

  def hasGenre(self, genre: str) -> bool:
    return genre in self.genres

class MovieData(object):
  def __init__(self,name):        # poziva se kod inicijalizacije
    self.name = name
    self.imdb_name = ""
    self.movieID = 0
    self.year = 0
    self.runtime = 0
    self.rating = 0.0
    self.directors = []
    self.genres = []
    self.short_cast = ""
    self.cast = []
    self.plot = ""
    self.producers = []
    self.writers = []
    self.box_office = ""
    
class FolderWithMovies(object):
  def __init__(self, folderName):
    self.name = folderName
    self.movies = []                # list of MovieData

  def loadData(self):
    movieSubFolders = [ f.name for f in os.scandir(self.name) if f.is_dir() ]

    for movieFolderName in movieSubFolders:
      if movieFolderName.find("IMDB") != -1:
        (imdb_name, year_str) = getNameYearFromNameWithIMDB(movieFolderName)
      
        if doesFilmDataHasMovieID(self.name, movieFolderName, imdb_name, int(year_str)) == True:
          movie_data = loadIMDBMovieDataFromFilmData(self.name, movieFolderName, imdb_name, int(year_str))

          self.movies.append(movie_data)

  def getMoviesWithRatingHigherThan(self, rating : float) :
    listMovies = [ movie for movie in self.movies if float(movie.rating) >= rating ]
    return listMovies

  def getMoviesWithRatingHigherThanWithGivenDirector(self, rating : float, director : str) :
    listMovies = [ movie for movie in self.movies if (float(movie.rating) >= rating and movie.isDirectedBy(director) == True) ]
    return listMovies

  def getMoviesWithRatingHigherThanWithGivenGenre(self, rating : float, genre: str) :
    listMovies = [ movie for movie in self.movies if (float(movie.rating) >= rating and movie.hasGenre(genre) == True) ]
    return listMovies

  # getMoviesDirectedBy
  # getMoviesWithActor# getMoviesWithGenre

class RootFolder(object):
  def __init__(self,rootFolderName : str):
    self.name = rootFolderName
    self.folders = []               # list of FolderWithMovies

  def loadData(self):
    rootSubFolders = [ f.path for f in os.scandir(self.name) if f.is_dir() ]

    for folderName in rootSubFolders:
      print("Adding - ", folderName)
      newFolder = FolderWithMovies(folderName)
      newFolder.loadData()
      self.folders.append(newFolder)

  def loadDataFromListOfFolders(self, listFolders):
    for folderName in listFolders:
      print("Adding - ", folderName)
      newFolder = FolderWithMovies(folderName)
      newFolder.loadData()
      self.folders.append(newFolder)

  def getMoviesWithRatingHigherThan(self, rating : float) :
    listMovies = []
    for folder in self.folders:
      listMovies += folder.getMoviesWithRatingHigherThan(rating)
    return listMovies

  def getMoviesWithRatingHigherThanWithGivenDirector(self, rating : float, director : str) :
    listMovies = []
    for folder in self.folders:
      listMovies += folder.getMoviesWithRatingHigherThanWithGivenDirector(rating, director)
    return listMovies

  def getMoviesWithRatingHigherThanWithGivenGenre(self, rating : float, genre : str) :
    listMovies = []
    for folder in self.folders:
      listMovies += folder.getMoviesWithRatingHigherThanWithGivenGenre(rating, genre)
    return listMovies

  def printMoviesWithRatingHigherThan(self, rating : float) :
    for folder in self.folders:
      newMovies = folder.getMoviesWithRatingHigherThan(rating)
      if len(newMovies) > 0 :
        print(folder.name)
        printMoviesList(newMovies)

  def printMoviesWithRatingHigherThanWithGivenDirector(self, rating : float, director : str) :
    for folder in self.folders:
      newMovies = folder.getMoviesWithRatingHigherThanWithGivenDirector(rating, director)
      if len(newMovies) > 0 :
        print(folder.name)
        printMoviesList(newMovies)

  def printMoviesWithRatingHigherThanWithGivenGenre(self, rating : float, genre : str) :
    for folder in self.folders:
      newMovies = folder.getMoviesWithRatingHigherThanWithGivenGenre(rating, genre)
      if len(newMovies) > 0 :
        print(folder.name)
        printMoviesList(newMovies)

# create an instance of the Cinemagoer class
ia = Cinemagoer()


# FILE OPERATIONS
#region
def getFolderSize(start_path : str):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

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
  
  newDirName = prefix + str(movie_data.name).rstrip() + "  (" + str(movie_data.year) + ")" + " IMDB-" + str(movie_data.rating) + " " + movie_data.genres + " CAST - " + movie_data.cast
  
  return newDirName

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

    # TODO provjeriti da li već postoji dest dir
    #print("RENAMING - ", origDir, "   -   ", destDir)
    if os.path.isdir(destDir):
      print("\n\nDESTINATION DIR ALREADY EXISTS!!!!!!\n\n")
    else:
      print("RENAMING - ", origDir, destDir)
      os.rename(origDir, destDir)

    print()

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

def saveTXTWithMovieData(movie_data : IMDBMovieData, folderWhereItIs, movieFolderName):
  # formirati TXT datoteku s podacima
  fileName = getFilmDataFilePath(folderWhereItIs, movieFolderName, movie_data.name, movie_data.year)

  fileFilmData = open(fileName, 'w')
  fileFilmData.write(movie_data.name + " (" + str(movie_data.year) + ")\n")
  fileFilmData.write("MovieID:   " + str(movie_data.movieID) + "\n")
  fileFilmData.write("Title:     " + movie_data.imdb_name + "\n")
  fileFilmData.write("Year:      " + str(movie_data.year) + "\n")
  fileFilmData.write("Runtime:   " + str(movie_data.runtime) + " min\n")
  fileFilmData.write("Rating:    " + str(movie_data.rating) + "\n")
  fileFilmData.write("Votes:     " + str(movie_data.votes) + "\n")
  fileFilmData.write("Genres:    " + movie_data.genres + "\n")
  fileFilmData.write("Directors: " + movie_data.directors + "\n")
  fileFilmData.write("Producers: " + movie_data.producers + "\n")
  fileFilmData.write("Writers:   " + movie_data.writers + "\n")
  fileFilmData.write("Box office:" + str(movie_data.box_office) + "\n")
  fileFilmData.write("Cast:      " + movie_data.cast_complete + "\n")
  fileFilmData.write("Plot:      " + str(movie_data.plot))

  fileFilmData.close()
 
def loadIMDBMovieDataFromFilmData(folderWhereItIs, movieFolderName, movieName, movieYear) -> IMDBMovieData:
  movie_data = IMDBMovieData(movieName)

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
    elif line.startswith("Runtime:"):
      ind = line.find("min")
      runtime = line[10:ind-1].strip()
      movie_data.runtime = runtime
    elif line.startswith("Rating:"):
      rating = line[10:].strip()
      movie_data.rating = rating
    elif line.startswith("Genres:"):
      genres = line[10:].strip()
      movie_data.genres = genres
    elif line.startswith("Directors:"):
      directors = line[10:].strip()
      movie_data.directors = directors
    elif line.startswith("Producers:"):
      producers = line[10:].strip()
      movie_data.producers = producers
    elif line.startswith("Writers:"):
      writers = line[10:].strip()
      movie_data.writers = writers
    elif line.startswith("Cast:"):
      cast = line[10:].strip()
      movie_data.cast_complete = cast
    elif line.startswith("Plot:"):
      plot = line[10:].strip()
      movie_data.plot = plot
    
  if movie_data.rating == 0.0:
    movie_data.rating = getRatingFromIMDBFolderName(movieFolderName)

  if movie_data.year == 0:
    movie_data.year = getYearFromIMDBFolderName(movieFolderName)

  return movie_data
#endregion


# fetchMovieData(searchMovieName, releaseYear)
def fetchMovieData(searchMovieName, releaseYear) -> IMDBMovieData:
  movie_data = IMDBMovieData(searchMovieName)

  searchMovieName = searchMovieName.rstrip()

  # TODO kad internet zakaže
  try:
    foundMoviesList = ia.search_movie(searchMovieName)
  except:
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    time.sleep(30)
    movie_data.name = ""
    return movie_data

  if len(foundMoviesList) == 0 :
    movie_data.name = ""
    print ("SEARCH RETURNED NOTHING!!!\n")
    return movie_data

  movieID = foundMoviesList[0].movieID
  movieFound = False
  for m in foundMoviesList:
    try:
      t = m.data.get('title')
      y = m.data.get('year')
      if t == searchMovieName and y == releaseYear:
        movieID = m.movieID
        movieFound = True
        break
    except:
      print("OUCH")
  
  if movieFound == False:
    print ("COULD FIND MOVIE WITH NAME AND YEAR") 
    for movie in foundMoviesList:
      print("-- {0:15} -- {1:30}, {2}".format(movie.movieID, movie.data.get('title'), movie.data.get('year')))
    #movie_data.name = ""
    #return movie_data

  try:
    movie = ia.get_movie(movieID)
  except:
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    time.sleep(30)
    movie_data.name = ""
    return movie_data
  
  time.sleep(5+random.randrange(0,5))

  movie_data.movieID = movieID

  try:
    movie_data.imdb_name = movie.data.get('title')

    rating = movie.data.get('rating', None)
    movie_data.rating = rating
    print("IMDB rating {0}".format(rating))

    votes = movie.data.get('votes', 0)
    movie_data.votes = votes
    print("Num. votes {0}".format(votes))

    box_office = movie.data.get('box office', None)
    movie_data.box_office = box_office
    print("Box office {0}".format(box_office))

    year = movie.data.get('year', None)
    movie_data.year = year
    print("Year: {0}".format(year))

    if 'runtimes' in movie.data:
      runtime = int(movie.data['runtimes'][0])
      movie_data.runtime = runtime
      print("Runtime: ", runtime, " min")
    else:
      print("-------------------------------------------")
      print("NO RUNTIME!!!!")
      print("-------------------------------------------")
      movie_data.runtime = 0

    directors = ""
    cntDir = 0
    if 'director' in movie.data:
      movieDirectors = movie.data.get('director')
      for director in movieDirectors:
          if cntDir > 0 :
            directors += ", "
          directors += director['name']
          cntDir += 1
    else:
      directors = " Problem with directors!!! "
    movie_data.directors = directors
    print("Directors: " + directors)

    producers = ""
    cntProd = 0
    if 'producer' in movie.data:
      movieProducers = movie.data.get('producer')
      for producer in movieProducers:
          if cntProd > 0 :
            producers += ", "

          if 'name' in producer:
            producers += producer['name']
          cntProd += 1

          if cntProd > 5:
            break
    else:
      producers = " Problem with producers!!! "
    movie_data.producers = producers
    print("Producers: " + producers)

    writers = ""
    cntWrit = 0
    if 'writer' in movie.data:
      movieWriters = movie.data.get('writer')
      for writer in movieWriters:
          if cntWrit > 0 :
            writers += ", "

          if 'name' in writer:
            writers += writer['name']
          cntWrit += 1
    else:
      writers = " Problem with writers!!! "
    movie_data.writers = writers
    print("Writers: " + writers)

    genres = ""
    shortGenres = ""
    cntGen = 0
    for gen in movie.data['genres']:
      genres += gen + ", "
      if cntGen > 0 and cntGen <3 :
        shortGenres += ","
      if cntGen < 3:
        shortGenres += gen

      cntGen += 1
    movie_data.genres = genres
    print('Genres: ' + genres)

    cast = ""
    shortCast = ""
    if 'cast' in movie.data:
      i = 0
      for actor in movie.data['cast']:
  #    for i in range(0,len(movie.data['cast'])-1):
        #s = movie.data['cast'][i]
        cast += actor['name']
        cast += ", "
        if i < 5 :
          shortCast += actor['name']
        if i >= 0 and i < 4 :
          shortCast += ", "
        i = i + 1
              
      print('Cast: ' + shortCast)
      movie_data.cast_complete = cast
      movie_data.cast = shortCast
    else:
      print("-------------------------------------------")
      print("NO CAST!!!")
      print("-------------------------------------------")
        
    print ()
    plot = movie.data.get('plot outline', None)
    movie_data.plot = plot
    #print("Plot outline: " + str(plot))

  except:
    print("\nERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!\n")
    movie_data.name = ""

  return movie_data
    
def fetchMovieDataByMovieID(movieID : str) -> IMDBMovieData:
  movie_data = IMDBMovieData()

  return movie_data

def processFolder(folderName):
  print("------------------------------------------")
  print("------", folderName, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

  fileErrors = open(folderName + "\\FileErrors.txt",'w', encoding="utf-8") 

  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") == -1:
      print(movieFolderName)

      (searchMovieName, year) = getMovieNameFromFolder(movieFolderName)

      movie_data = fetchMovieData(searchMovieName, year)
    
      if movie_data.name != "":
        saveMovieDataAndRenameFolder(movie_data,folderName,movieFolderName)


def folderRecheckDataWithIMDB(folderName):
  print("------", folderName, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") != -1:
      ind1 = movieFolderName.find("(")
      ind2 = movieFolderName.find(")")
      imdb_name_raw = movieFolderName[0:ind1-1]
      if imdb_name_raw.startswith("zzz"):
        imdb_name1 = movieFolderName[4:ind1-1]
      else:
        imdb_name1 = imdb_name_raw
      imdb_name = imdb_name1.strip("_")
      year_str  = movieFolderName[ind1+1:ind2]
      
      # TODO - provjeriti ima li movieID,ako ima, onda nista
      if doesFilmDataHasMovieID(folderName, movieFolderName, imdb_name, int(year_str)) :
        continue

      print("-----------------------------------------------------")
      print("\nReal movie name: " + imdb_name)
      print("Year           : " + year_str)
      movie_data = fetchMovieData(imdb_name, int(year_str))

      if movie_data.name == "":
        print("SLEEPING 5-10 seconds :(((((")
        time.sleep(5 + random.randrange(0,5))
      else:
        # produce novi naziv direktorija
        newDirName = getMovieFolderNameFromMovieData(movie_data)

        # usporedi s movieFileName
        if newDirName != movieFolderName:
          print("AHAAAA")
          print(newDirName)
          print(movieFolderName)

          # formirati TXT datoteku s podacima
          saveTXTWithMovieData(movie_data, folderName, movieFolderName)

          # i sad idemo preimenovati direktorij
          origDir = folderName + "\\" + movieFolderName
          destDir = folderName + "\\" + newDirName

          # provjeriti da li već postoji dest dir
          if os.path.isdir(destDir):
            print("\n\nDESTINATION DIR ALREADY EXISTS!!!!!!\n\n")
          else:
            print("RENAMING - ", origDir, destDir)
            os.rename(origDir, destDir)
        else:
          saveTXTWithMovieData(movie_data, folderName, movieFolderName)


        time.sleep(5 + random.randrange(0,5))

# Folder statistics
#region

def folderStatistics(folderName):
  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]
  
  cntNotDone = 0
  cntImdb8 = 0
  cntImdb7 = 0
  cntImdbLower6 = 0

  listNotDone = []
  listWithoutMovieID = []

  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") != -1:
      (imdb_name, year_str) = getNameYearFromNameWithIMDB(movieFolderName)

      ind = movieFolderName.find("IMDB")
      imdb_rat = movieFolderName[ind+5:ind+8]
      
      if float(imdb_rat) >= 8.0:
        cntImdb8 = cntImdb8 + 1
      elif float(imdb_rat) >= 7.0:
        cntImdb7 = cntImdb7 + 1
      elif float(imdb_rat) < 6.0:
        cntImdbLower6 = cntImdbLower6 + 1

      if doesFilmDataHasMovieID(folderName, movieFolderName, imdb_name, int(year_str)) == False:
        listWithoutMovieID.append(movieFolderName)
    else:
      cntNotDone = cntNotDone + 1
      listNotDone.append(movieFolderName)

  #if cntNotDone == 0:
  #  return

  print("-- {0:65} -- {1:2}, {2:2}, {3:3}, {4:2}, {5:2}, {6:2}".format(folderName, cntNotDone, cntImdb8, cntImdb7, cntImdbLower6, len(listNotDone), len(listWithoutMovieID)))
  
  #if len(listNotDone) > 0:
  #  print("LIST NOT DONE:")
  #  for movie in listNotDone: 
  #    print ("  ", movie)

  #if len(listWithoutMovieID) > 0:
  #  print("LIST WITHOUT MOVIE ID:")
  #  for movie in listWithoutMovieID:
  #    print ("  ", movie)

def folderSizeStatistic(folderName):
  print("------------------------------------------")
  print("------", folderName, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") != -1:
      size = getFolderSize(folderName + "\\" + movieFolderName)
      printName = movieFolderName[0:60]
      print("{0:60} - {1}".format(printName, size / 1000000000))
#endregion

# Underscore functionality
#region
# UNDERSCORE RATING
def setFolderNameUnderscoreRating(folderName, movieFolderName, imdbRating):
  m1 = movieFolderName.strip("zzz")
  realMovieName = m1.strip("_")

  # strip sve underscore na poečtku
  if imdbRating >= 9.0:
    origDir = folderName + "\\" + movieFolderName
    destDir = folderName + "\\" + "___" + realMovieName
    print("RENAMING - ", origDir, destDir)
    os.rename(origDir, destDir)
  elif imdbRating >= 8.0:
    origDir = folderName + "\\" + movieFolderName
    destDir = folderName + "\\" + "__" + realMovieName
    print("RENAMING - ", origDir, " -> ", destDir)
    os.rename(origDir, destDir)
  elif imdbRating >= 7.0:
    origDir = folderName + "\\" + movieFolderName
    destDir = folderName + "\\" + "_" + realMovieName
    print("RENAMING - ", origDir, destDir)
    os.rename(origDir, destDir)
  elif imdbRating >= 6.0:
    origDir = folderName + "\\" + movieFolderName
    destDir = folderName + "\\" + realMovieName
    print("RENAMING - ", origDir, destDir)
    os.rename(origDir, destDir)
  elif imdbRating < 6.0:
    origDir = folderName + "\\" + movieFolderName
    destDir = folderName + "\\" + "zzz_" + realMovieName
    print("RENAMING - ", origDir, destDir)
    os.rename(origDir, destDir)

def folderReapplyUnderscoreRating(folderName):
  print("------", folderName, "------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]
  
  listNotDone = []
  for movieFileName in movieSubFolders:
    if movieFileName.find("IMDB") != -1:
      ind = movieFileName.find("IMDB")
      imdb_rat_str = movieFileName[ind+5:ind+8]
      imdb_rat = float(imdb_rat_str)
      
      ind = movieFileName.find("(")
      imdb_name = movieFileName[0:ind-1]

      underscore_rat = 0
      if imdb_name.startswith("___"):
        if imdb_rat < 9.0:
          print("ERRROR - ", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
      elif imdb_name.startswith("__"):
        if imdb_rat < 8.0:
          print("ERRROR - ", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
        elif imdb_rat >= 9.0:
          print("ERROR - SHOULD BE HIGHER", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
      elif imdb_name.startswith("_"):
        if imdb_rat < 7.0:
          print("ERRROR - ", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
        elif imdb_rat >= 8.0:
          print("ERROR - SHOULD BE HIGHER", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
      elif imdb_name.startswith("_") == False and imdb_rat >= 7.0:
        print("ERROR - SHOULD BE HIGHER", movieFileName)
        setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
      elif imdb_name.startswith("zzz_"):
        if imdb_rat >= 6.0:
          print("ERRROR - ", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)

# UNDERSCORE STATISTICS
def folderUnderscoreStatistics(folderName):
  print("------", folderName, "------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]
  
  listNotDone = []
  for movieFileName in movieSubFolders:
    if movieFileName.find("IMDB") != -1:
      ind = movieFileName.find("IMDB")
      imdb_rat_str = movieFileName[ind+5:ind+8]
      imdb_rat = float(imdb_rat_str)
      ind = movieFileName.find("(")
      imdb_name = movieFileName[0:ind-1]

      underscore_rat = 0
      if imdb_name.startswith("___"):
        if imdb_rat < 9.0:
          print("ERRROR - ", movieFileName)
      elif imdb_name.startswith("__"):
        if imdb_rat < 8.0:
          print("ERRROR - ", movieFileName)
        elif imdb_rat >= 9.0:
          print("ERROR - SHOULD BE HIGHER", movieFileName)
      elif imdb_name.startswith("_"):
        if imdb_rat < 7.0:
          print("ERRROR - ", movieFileName)
        elif imdb_rat >= 8.0:
          print("ERROR - SHOULD BE HIGHER", movieFileName)
      elif imdb_name.startswith("_") == False and imdb_rat >= 7.0:
        print("ERROR - SHOULD BE HIGHER", movieFileName)
      elif imdb_name.startswith("zzz_"):
        if imdb_rat >= 6.0:
          print("ERRROR - ", movieFileName)
        
def rootFolderUnderscoreStatistics(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  for folderName in rootSubFolders:
    folderUnderscoreStatistics(folderName)
 #endregion

 # Root folder reports
def rootFolderReportNotDone(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  for folderName in rootSubFolders:
    movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]
  
    cntNotDone = 0
    listNotDone = []

    for movieFolderName in movieSubFolders:
      if movieFolderName.find("IMDB") == -1:
        cntNotDone = cntNotDone + 1
        listNotDone.append(movieFolderName)

    if cntNotDone == 0:
      continue

    print("-- {0:65} -- {1:2}, {2:2} ".format(folderName, cntNotDone, len(listNotDone) ))
  
    if len(listNotDone) > 0:
      print("LIST NOT DONE:")
      for movie in listNotDone: 
        print ("  ", movie)

def rootFolderReportNoIMDBData(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  for folderName in rootSubFolders:
    movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]
  
    listWithoutMovieID = []

    for movieFolderName in movieSubFolders:
      if movieFolderName.find("IMDB") != -1:
        (imdb_name, year_str) = getNameYearFromNameWithIMDB(movieFolderName)

        if doesFilmDataHasMovieID(folderName, movieFolderName, imdb_name, int(year_str)) == False:
          listWithoutMovieID.append(movieFolderName)

    if len(listWithoutMovieID) == 0:
      continue

    print("-- {0:65} -- {1:2}".format(folderName, len(listWithoutMovieID)))
  
    if len(listWithoutMovieID) > 0:
      print("LIST WITHOUT MOVIE ID:")
      for movie in listWithoutMovieID:
        print ("  ", movie)


# Root folder iterators - Statistics & RecheckDataWithIMDB
def rootFolderStatistics(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  for folderName in rootSubFolders:
    folderStatistics(folderName)

def rootFolderRecheckDataWithIMDB(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  for folderName in rootSubFolders:
    folderRecheckDataWithIMDB(folderName)

def printMoviesList(listMovies):
  for movie in listMovies:
    short_cast = movie.cast_complete[0:50]
    print("Rating - {0} - {1:40} - {2}        -   {3:30}   - {4}".format( movie.rating, movie.name + " (" + str(movie.year) + ") ", short_cast, movie.directors, movie.genres ) )

def getSeriesFolderNames():
  listNames = []
  startFolder = "Z:\Movies\FILMOVI"
  subFolders= [ f.name for f in os.scandir(startFolder) if f.is_dir() ]

  for folderName in subFolders:
    if folderName.startswith("_") == True and folderName.startswith("__") == False and folderName.startswith("___") == False and folderName.startswith("____") == False :
      if folderName[2] >= '0' and folderName[2] <= '9' :
        continue
      else:
        listNames.append(startFolder + "\\" + folderName)
        print(folderName)

  return listNames

def getMiscDirectorsList():
  startFolder = otherDirectorsFolder
  listDirectors = [ f.name for f in os.scandir(startFolder) if f.is_dir() ]

  return listDirectors

def printBigFiles():
  # The min size of the file in Bytes
  mySize = '1000000000'

  startFolder = "Z:\Movies\FILMOVI"
  subFolders= [ f.name for f in os.scandir(startFolder) if f.is_dir() ]

  countTotal = 0
  for folderName in subFolders:
    myPath = os.path.join(startFolder, folderName)
    count = 0
    for path, subdirs, files in os.walk(myPath):
      for name in files:
        filePath = os.path.join(path, name)
        fileSize = os.path.getsize(filePath)

        if int(fileSize) >= int(mySize):
            count += 1
            countTotal += 1
    
    print("{0:75} - {1:3}".format(myPath , count))

  print("TOTAL = " + str(countTotal))

#printBigFiles()


#seriesFolders = getSeriesFolderNames()
#root = RootFolder("Test series")
#root.loadDataFromListOfFolders(seriesFolders) 

#processFolder("Z:\Movies\FILMOVI\__Christopher Nolan")
#processFolder("D:\Downloads\ROMANCE MOVIES")
#processFolder("Z:\Movies\FILMOVI\__Stanley Kubrick")
#processFolder("Z:\Movies\FILMOVI\__Quentin Tarantino")


#root = RootFolder("Other directors")
#root.loadDataFromListOfFolders(seriesFolders) 
#root.loadDataFromListOfFolders(actorsFolders + decadesFolders + genresFolders) 
#listDir = getMiscDirectorsList()
#for dir in listDir:
#  root.printMoviesWithRatingHigherThanWithGivenDirector(5.0, dir)

#root = RootFolder("Test directors")
#root.loadDataFromListOfFolders(directorsFolders) 
#root = RootFolder("Test genres")
#root.loadDataFromListOfFolders(genresFolders)
#root = RootFolder("Test actors")
#root.loadDataFromListOfFolders(actorsFolders)
#root = RootFolder("Test decades")
#root.loadDataFromListOfFolders(decadesFolders)

#root = RootFolder("Test actors")
#root.loadDataFromListOfFolders(decadesFolders)

#root.printMoviesWithRatingHigherThanWithGivenGenre(7.0, "Romance")
#root.printMoviesWithRatingHigherThanWithGivenDirector(5.0, "Ridley Scott")


#for director in directorsList:
#  root.printMoviesWithRatingHigherThanWithGivenDirector(5.0, director)

#printMoviesList(list1)


#folderStatistics("Z:\Movies\FILMOVI\___1970's")

#rootFolderRecheckDataWithIMDB("Z:\Movies\FILMOVI")
#rootFolderReportNoIMDBData("Z:\Movies\FILMOVI")

#rootFolderStatistics("Z:\Movies\FILMOVI")
#rootFolderReportNotDone("Z:\Movies\FILMOVI")
processFolder("Z:\Movies\FILMOVI\_____GOOD DONE")

#folderSizeStatistic("Z:\Movies\FILMOVI\___Westerns")

# TODO
# dodati konstante na pocetku
# analyze folder
#   prikupi FilmData i ispiše statistike
# copy empty folder names - 
#   Directors -> Actors, po godinama
# doesContainMovie za folder
# ucitavanje podataka o filmu iz Film data
# analiza velicine direktorija (a mozda ima i vise verzija!)
#   ispis manjih od 2 Gb

# dodati podatke o budgetu i zaradi
# dodati awards - Best Picture Osar
# writer, producer
# dodati person id

# proći kroz sve IMDB, i provjeriti da li se naziv direktorija slaže, s onim kako bi sada bilo
# pocistiti file errors, RARBG.txt, i not mirror

# DONE - statistika - koji se sve ne slažu underscore s ocjenom
# DONE - provjeriti da li postoji movieID


