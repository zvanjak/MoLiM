from re import search
from shutil import move
from sys import orig_argv
from typing import Tuple
from xmlrpc.client import Boolean
from imdb import Cinemagoer

from datetime import date

import time
import random
import os
import tkinter

import fileOperations 
import IMDBMovieData 
import imdbAccess

otherActorsFolder = "Z:\Movies\FILMOVI\___00_Actors_others"
otherDirectorsFolder = "Z:\Movies\FILMOVI\__00_Directors_others"

directorsFolders = [ "Z:\Movies\FILMOVI\__Akira Kurosawa",       \
  "Z:\Movies\FILMOVI\__Alfred Hitchcock",       \
  "Z:\Movies\FILMOVI\__Christopher Nolan",      \
  "Z:\Movies\FILMOVI\__Coen brothers",          \
  "Z:\Movies\FILMOVI\__John Ford",              \
  "Z:\Movies\FILMOVI\__Martin Scorsese",        \
  "Z:\Movies\FILMOVI\__Quentin Tarantino",      \
  "Z:\Movies\FILMOVI\__Ridley Scott",           \
  "Z:\Movies\FILMOVI\__Stanley Kubrick",        \
  "Z:\Movies\FILMOVI\__Steven Spielberg"
]  

directorsList = [ "Akira Kurosawa",     \
                  "Alfred Hitchcock",   \
                  "Christopher Nolan",  \
                  "Coen",      \
                  "John Ford",          \
                  "Martin Scorsese",    \
                  "Quentin Tarantino",  \
                  "Ridley Scott",       \
                  "Stanley Kubrick",    \
                  "Steven Spielberg" ]

actorsFolders = [ "Z:\Movies\FILMOVI\___Al Pacino",   \
  "Z:\Movies\FILMOVI\___Brad Pitt",                   \
  "Z:\Movies\FILMOVI\___Bruce Lee",                   \
  "Z:\Movies\FILMOVI\___Clint Eastwood",              \
  "Z:\Movies\FILMOVI\___Humphrey Bogart",             \
  "Z:\Movies\FILMOVI\___Jack Nicholson",              \
  "Z:\Movies\FILMOVI\___John Wayne",                  \
  "Z:\Movies\FILMOVI\___Leonardo DiCaprio",           \
  "Z:\Movies\FILMOVI\___Mel Gibson",                  \
  "Z:\Movies\FILMOVI\___Robert De Niro",              \
  "Z:\Movies\FILMOVI\___Spencer Tracy",               \
  "Z:\Movies\FILMOVI\___Tom Cruise",                  \
  "Z:\Movies\FILMOVI\___Tom Hanks"
]  

actorsList = [ "Al Pacino",      \
  "Brad Pitt",                   \
  "Bruce Lee",                   \
  "Clint Eastwood",              \
  "Humphrey Bogart",             \
  "Jack Nicholson",              \
  "John Wayne",                  \
  "Leonardo DiCaprio",           \
  "Mel Gibson",                  \
  "Robert De Niro",              \
  "Tom Cruise",                  \
  "Tom Hanks",
] 

genresFolders = [ "Z:\Movies\FILMOVI\____Action, Crime & Thriller",       \
  "Z:\Movies\FILMOVI\____Adventure",       \
  "Z:\Movies\FILMOVI\____Biography & History",       \
  "Z:\Movies\FILMOVI\____Comedy",       \
  "Z:\Movies\FILMOVI\____Drama",       \
  "Z:\Movies\FILMOVI\____Europe & Asia movies",       \
  "Z:\Movies\FILMOVI\____Family fun",       \
  "Z:\Movies\FILMOVI\____Horrors",       \
  "Z:\Movies\FILMOVI\____Romance",       \
  "Z:\Movies\FILMOVI\____Science Fiction & Fantasy",       \
  "Z:\Movies\FILMOVI\____War movies",       \
  "Z:\Movies\FILMOVI\____Westerns"
]  

decadesFolders = [ "Z:\Movies\FILMOVI\_1920-40's",       \
  "Z:\Movies\FILMOVI\_1950's",       \
  "Z:\Movies\FILMOVI\_1960's",       \
  "Z:\Movies\FILMOVI\_1970's",       \
  "Z:\Movies\FILMOVI\_1980's",       \
  "Z:\Movies\FILMOVI\_1990's",       \
  "Z:\Movies\FILMOVI\_2000's",       \
  "Z:\Movies\FILMOVI\_2010's",       \
  "Z:\Movies\FILMOVI\_2020's"
]  


def getMiscDirectorsList():
  startFolder = otherDirectorsFolder
  listDirectors = [ f.name for f in os.scandir(startFolder) if f.is_dir() ]

  return listDirectors

def getMiscActorsList():
  startFolder = otherActorsFolder
  listActors = [ f.name for f in os.scandir(startFolder) if f.is_dir() ]

  return listActors 


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


class FolderWithMovies(object):
  def __init__(self, folderName):
    self.name = folderName
    self.movies = []                # list of MovieData

  def loadData(self):
    movieSubFolders = [ f.name for f in os.scandir(self.name) if f.is_dir() ]

    for movieFolderName in movieSubFolders:
      if movieFolderName.find("IMDB") != -1:
        (imdb_name, year_str) = getNameYearFromNameWithIMDB(movieFolderName)
      
        if doesFilmDataHasMovieID(self.name, movieFolderName, imdb_name, int(year_str)) == True :
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

  def getMoviesWithRatingHigherThanWithGivenActor(self, rating : float, actor: str) :
    listMovies = [ movie for movie in self.movies if (float(movie.rating) >= rating and movie.hasActor(actor) == True) ]
    return listMovies
  
class RootFolder(object):
  def __init__(self, rootFolderName : str):
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
      newMovies = folder.getMoviesWithRatingHigherThanWithGivenDirector(rating, director)
      for newMovie in newMovies:
        if next((x for x in listMovies if x.name == newMovie.name),None) == None:
          listMovies.append(newMovie)

    return listMovies

  def getMoviesWithRatingHigherThanWithGivenGenre(self, rating : float, genre : str) :
    listMovies = []
    for folder in self.folders:
      newMovies = folder.getMoviesWithRatingHigherThanWithGivenGenre(rating, genre)
      for newMovie in newMovies:
        if next((x for x in listMovies if x.name == newMovie.name),None) == None:
          listMovies.append(newMovie)

    return listMovies

  def getMoviesWithRatingHigherThanWithGivenActor(self, rating : float, actor : str) :
    listMovies = []
    for folder in self.folders:
      newMovies = folder.getMoviesWithRatingHigherThanWithGivenActor(rating, actor)
      for newMovie in newMovies:
        if next((x for x in listMovies if x.name == newMovie.name),None) == None:
          listMovies.append(newMovie)

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

  def printMoviesWithRatingHigherThanWithGivenActor(self, rating : float, actor : str) :
    for folder in self.folders:
      newMovies = folder.getMoviesWithRatingHigherThanWithGivenActor(rating, actor)
      if len(newMovies) > 0 :
        print(folder.name)
        printMoviesList(newMovies)

# create an instance of the Cinemagoer class
ia = Cinemagoer()


def processFolder(folderName):
  print("------------------------------------------")
  print("------", folderName, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") == -1:
      print(movieFolderName)

      (searchMovieName, year) = getMovieNameFromFolder(movieFolderName)

      movie_data = imdbAccess.fetchMovieData(searchMovieName, year)
    
      if movie_data.name != "":
        saveMovieDataAndRenameFolder(movie_data,folderName,movieFolderName)

def processListOfFolders(foldersList):
  for folderName in foldersList:
    print("------------------------------------------")
    print("------", folderName, "------")
    print("------------------------------------------")

    movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

    for movieFolderName in movieSubFolders:
      if movieFolderName.find("IMDB") == -1:
        print(movieFolderName)

        (searchMovieName, year) = getMovieNameFromFolder(movieFolderName)

        movie_data = imdbAccess.fetchMovieData(searchMovieName, year)
    
        if movie_data.name != "":
          saveMovieDataAndRenameFolder(movie_data,folderName,movieFolderName)

# Rechecking IMDB data
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
      movie_data = imdbAccess.fetchMovieData(imdb_name, int(year_str))

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

def rootFolderRecheckDataWithIMDB(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  for folderName in rootSubFolders:
    folderRecheckDataWithIMDB(folderName)

# Folder statistics
#region  

def folderStatistics(folderName):
  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]
  
  cntNotDone = 0
  cntImdb9 = 0
  cntImdb8 = 0
  cntImdb7 = 0
  cntImdb6 = 0
  cntImdbLower6 = 0

  listNotDone = []
  listWithoutMovieID = []

  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") != -1:
      (imdb_name, year_str) = getNameYearFromNameWithIMDB(movieFolderName)

      ind = movieFolderName.find("IMDB")
      imdb_rat = movieFolderName[ind+5:ind+8]
      
      if float(imdb_rat) >= 9.0:
        cntImdb9 +=  1
      elif float(imdb_rat) >= 8.0:
        cntImdb8 += 1
      elif float(imdb_rat) >= 7.0:
        cntImdb7 += 1
      elif float(imdb_rat) >= 6.0:
        cntImdb6 += 1
      elif float(imdb_rat) < 6.0:
        cntImdbLower6 += 1

      if doesFilmDataHasMovieID(folderName, movieFolderName, imdb_name, int(year_str)) == False:
        listWithoutMovieID.append(movieFolderName)
    else:
      cntNotDone = cntNotDone + 1
      listNotDone.append(movieFolderName)

  #if cntNotDone == 0:
  #  return

  print("-- {0:65} -- {1:3}, {2:3}, {3:3}, {4:3}, {5:3}   -- {6:2}, {7:2}".format(folderName, cntImdb9, cntImdb8, cntImdb7, cntImdb6, cntImdbLower6, len(listNotDone), len(listWithoutMovieID)))
  
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

def rootFolderStatistics(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  for folderName in rootSubFolders:
    folderStatistics(folderName)

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


def printMoviesList(listMovies):
  for movie in listMovies:
    short_cast = movie.cast_complete[0:75]
    short_dir = movie.directors[0:20]
    print("Rating - {0} - {1:55} - {2:75}  -  {3:20}  - {4}".format( movie.rating, movie.name + " (" + str(movie.year) + ") ", short_cast, short_dir, movie.genres ) )

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


def printDirectorsStatistics():
  root = RootFolder("Directors")
  seriesFolders = getSeriesFolderNames()
  listDirectors = getMiscDirectorsList() + directorsList
  listDirectors.sort()
#  root.loadDataFromListOfFolders(directorsFolders + actorsFolders + genresFolders + decadesFolders +  seriesFolders) 
  root.loadDataFromListOfFolders(actorsFolders + genresFolders + decadesFolders + directorsFolders + ["E:\DONE", "Z:\Movies\FILMOVI\_____GOOD DONE"] + seriesFolders) 

  tuplesList = []

  for director in listDirectors:
    listMovies = root.getMoviesWithRatingHigherThanWithGivenDirector(5.0, director)
    listMovies.sort(key=lambda x: x.rating, reverse=True)
    if len(listMovies) > 0:
      sum = 0.0
      for movie in listMovies[0:10]:
        sum += movie.rating
      newTuple = (director, sum / len(listMovies[0:10]) )
      tuplesList.append(newTuple)
    else:
      print("     -----------------                   NO MOVIES FOR DIRECTOR - ", director)

  tuplesList.sort(key=lambda x: x[1], reverse=True)

  ordNum = 0
  for tup in tuplesList:
    director = tup[0]
    ordNum += 1
    print("-----------------------------------------------------------------")
    print("{0} - DIRECTOR - {1}".format(ordNum, director) )
    print("-----------------------------------------------------------------")

    listMovies = root.getMoviesWithRatingHigherThanWithGivenDirector(5.0, director)
    listMovies.sort(key=lambda x: x.rating, reverse=True)
    printMoviesList(listMovies[0:10])
    print("AVG = ", tup[1])

def printActorsStatistics():
  root = RootFolder("Other actors")
  seriesFolders = getSeriesFolderNames()
  listActors = getMiscActorsList() + actorsList
  listActors.sort()
  root.loadDataFromListOfFolders(actorsFolders + genresFolders + decadesFolders + directorsFolders + ["E:\DONE", "Z:\Movies\FILMOVI\_____GOOD DONE"] + seriesFolders) 

  tuplesList = []

  for actor in listActors:
    listMovies = root.getMoviesWithRatingHigherThanWithGivenActor(5.0, actor)
    listMovies.sort(key=lambda x: x.rating, reverse=True)
    if len(listMovies) > 0:
      sum = 0.0
      for movie in listMovies[0:10]:
        sum += movie.rating
      newTuple = (actor, sum / len(listMovies[0:10]) )
      tuplesList.append(newTuple)
    else:
      print("     -----------------                   NO MOVIES FOR ACTOR - ", actor)

  tuplesList.sort(key=lambda x: x[1], reverse=True)

  ordNum = 0
  for tup in tuplesList:
    actor = tup[0]
    ordNum += 1
    print("-----------------------------------------------------------------")
    print("{0} - ACTOR - {1}".format(ordNum, actor) )
    print("-----------------------------------------------------------------")

    listMovies = root.getMoviesWithRatingHigherThanWithGivenActor(5.0, actor)
    listMovies.sort(key=lambda x: x.rating, reverse=True)
    printMoviesList(listMovies[0:10])
    print("AVG = ", tup[1])


def printDecadesStatistics(folderName):
  print("------------------------------------------")
  print("------", folderName, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

  decadeCount = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  
  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") != -1:
      (searchMovieName, year) = getNameYearFromNameWithIMDB(movieFolderName)

      decade = int(int(year) / 10) - 192
      decadeCount[decade] += 1

  decadeStart = 1920
  for dec in decadeCount:
    print("Decade {0} - {1} : {2}".format(decadeStart, decadeStart + 10, dec))
    decadeStart += 10


def printRootDecadesStatistics(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  decadeCount = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  
  for folderName in rootSubFolders:
    print(folderName)
    movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

    for movieFolderName in movieSubFolders:
      if movieFolderName.find("IMDB") != -1:
        
        (searchMovieName, year) = fileOperations.getNameYearFromNameWithIMDB(movieFolderName)

        decade = int(int(year) / 10) - 192
        decadeCount[decade] += 1

  decadeStart = 1920
  for dec in decadeCount:
    print("Decade {0} - {1} : {2}".format(decadeStart, decadeStart + 10, dec))
    decadeStart += 10

def copyDirectors(foldersList):
  root = RootFolder("Copy")
  listDirectors = getMiscDirectorsList() + directorsList
  listDirectors.sort()
  
  for folder in foldersList:
    print("--------------------------------------------")
    print(folder)
    print("--------------------------------------------")

    folderObj = FolderWithMovies(folder)
    folderObj.loadData()

    for director in listDirectors:
      listMovies = folderObj.getMoviesWithRatingHigherThanWithGivenDirector(5.0, director)
      if len(listMovies) > 0:
        print(director)
        printMoviesList(listMovies)
      #for movie in listMovies:
        # treba mi lista foldera za svakog directora
        #print("FROM - ")


def reprocessFolderIMDBData(folderName):
  print("------------------------------------------")
  print("------", folderName, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") != -1:
      print(movieFolderName)

      (searchMovieName, year) = getNameYearFromNameWithIMDB(movieFolderName)

      movieID = getMovieIDFromFilmData(folderName, movieFolderName, searchMovieName, year)

      if movieID != None :
        print("Processing: " + searchMovieName, "  (", year, ")")
        
        movie_data = imdbAccess.fetchMovieDataByMovieID(searchMovieName, movieID)

        if movie_data.name != "":
          saveTXTWithMovieData(movie_data, folderName, movieFolderName)

        time.sleep(2 + random.randrange(0,2))


printRootDecadesStatistics("Z:\Movies\FILMOVI")
#reprocessFolderIMDBData("Z:\Movies\FILMOVI\_Batman")

#movie = fetchMovieDataByMovieID("Good Will Hunting", "0119217")

#print(movie)

#copyDirectors(genresFolders)

#printActorsStatistics()
#printDirectorsStatistics()

#rootFolderStatistics("Z:\Movies\FILMOVI")
#folderStatistics("Z:\Movies\FILMOVI\_1970's")

#rootFolderReportNoIMDBData("Z:\Movies\FILMOVI")
#rootFolderReportNotDone("Z:\Movies\FILMOVI")

#printBigFiles()

#processFolder("E:\DONE")
#processFolder("Z:\Movies\FILMOVI\_____GOOD DONE")

#processListOfFolders( ("Z:\Movies\FILMOVI\_____GOOD DONE\Denis Vilenueve",          \
#                       "Z:\Movies\FILMOVI\_____GOOD DONE\Humphrey Bogart",      \
#                       #"Z:\Movies\FILMOVI\_____GOOD DONE\Jodie Foster",    \
#                       #"E:\Downloads\Marlon Brando",    \
#                       #"E:\Downloads\\Nicole Kidman",   \
#                       # "E:\Downloads\Sergio Leone",     \
#                       #"E:\Downloads\Sigourney Weaver", \
#                       #"E:\Downloads\Michelle Pfeiffer",  \
#                       #"E:\Downloads\Paul Newman",      \
#                       #"E:\Downloads\Sidney Lumet",     \
#                       "Z:\Movies\FILMOVI\_____GOOD DONE\Jodie Foster") )

#rootFolderRecheckDataWithIMDB("Z:\Movies\FILMOVI")


#seriesFolders = getSeriesFolderNames()
#root = RootFolder("Test series")
#root.loadDataFromListOfFolders(seriesFolders) 
#root.printMoviesWithRatingHigherThanWithGivenGenre(7.0, "Romance")
#root.printMoviesWithRatingHigherThanWithGivenDirector(5.0, "Ridley Scott")

#for director in directorsList:
#  root.printMoviesWithRatingHigherThanWithGivenDirector(5.0, director)


# TODO
# getAllMoviesByActor
# getAllMoviesByDirector
# getAllMoviesInGenre

# vidjeti za dodati MetaCritic i Tomatoes rating
# dodati konstante na pocetku

# copy empty folder names - 
#   proći kroz sve Genre direktorije
#     uzeti movieFolder
#     ucitati filmData
#     proci kroz directors list
#       ako je rezirao
#     proci kroz actors list
#     
#   Directors -> Actors, po godinama

# doesContainMovie za folder

# statistike po budžetu - najskuplji, najveći cumulative gross

# statistike imdb top 250 - koji mi fale

# pocistiti file errors, RARBG.txt, i not mirror

# DONE -------------------------------------------------------
# statistika - koji se sve ne slažu underscore s ocjenom
# provjeriti da li postoji movieID
# dodati podatke o budgetu i zaradi
# dodati awards - Best Picture Osar
# writer, producer
# dodati person id
# proći kroz sve IMDB, i provjeriti da li se naziv direktorija slaže, s onim kako bi sada bilo
# ucitavanje podataka o filmu iz Film data
# analiza velicine direktorija (a mozda ima i vise verzija!)
#   ispis manjih od 2 Gb

