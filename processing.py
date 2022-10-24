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

import fileOperations 
import IMDBMovieData 
import imdbAccess


def processFolder(folderName):
  print("------------------------------------------")
  print("------", folderName, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") == -1:
      print(movieFolderName)

      (searchMovieName, year) = fileOperations.getMovieNameFromFolder(movieFolderName)

      movie_data = imdbAccess.fetchMovieData(searchMovieName, year)
    
      if movie_data.name != "":
        fileOperations.saveMovieDataAndRenameFolder(movie_data,folderName,movieFolderName)

def processListOfFolders(foldersList):
  for folderName in foldersList:
    print("------------------------------------------")
    print("------", folderName, "------")
    print("------------------------------------------")

    movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

    for movieFolderName in movieSubFolders:
      if movieFolderName.find("IMDB") == -1:
        print(movieFolderName)

        (searchMovieName, year) = fileOperations.getMovieNameFromFolder(movieFolderName)

        movie_data = imdbAccess.fetchMovieData(searchMovieName, year)
    
        if movie_data.name != "":
          fileOperations.saveMovieDataAndRenameFolder(movie_data,folderName,movieFolderName)

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
      if fileOperations.doesFilmDataHasMovieID(folderName, movieFolderName, imdb_name, int(year_str)) :
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
        newDirName = fileOperations.getMovieFolderNameFromMovieData(movie_data)

        # usporedi s movieFileName
        if newDirName != movieFolderName:
          print("AHAAAA")
          print(newDirName)
          print(movieFolderName)

          # formirati TXT datoteku s podacima
          fileOperations.saveTXTWithMovieData(movie_data, folderName, movieFolderName)

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
          fileOperations.saveTXTWithMovieData(movie_data, folderName, movieFolderName)


        time.sleep(5 + random.randrange(0,5))

def rootFolderRecheckDataWithIMDB(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  for folderName in rootSubFolders:
    folderRecheckDataWithIMDB(folderName)



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

      (searchMovieName, year) = fileOperations.getNameYearFromNameWithIMDB(movieFolderName)

      movieID = getMovieIDFromFilmData(folderName, movieFolderName, searchMovieName, year)

      if movieID != None :
        print("Processing: " + searchMovieName, "  (", year, ")")
        
        movie_data = imdbAccess.fetchMovieDataByMovieID(searchMovieName, movieID)

        if movie_data.name != "":
          fileOperations.saveTXTWithMovieData(movie_data, folderName, movieFolderName)

        time.sleep(2 + random.randrange(0,2))
