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
      (imdb_name, year_str) = fileOperations.getNameYearFromNameWithIMDB(movieFolderName)

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

      if fileOperations.doesFilmDataHasMovieID(folderName, movieFolderName, imdb_name, int(year_str)) == False:
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
      size = fileOperations.getFolderSize(folderName + "\\" + movieFolderName)
      printName = movieFolderName[0:60]
      print("{0:80} - {1:5} Gb".format(printName, size / 1000000000))

def rootFolderStatistics(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  for folderName in rootSubFolders:
    folderStatistics(folderName)


def printBigFiles():
  # The min size of the file in Bytes
  mySize = '9000000000'
  minSize = '1000000000'
  maxSize = '9000000000'

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

        if int(fileSize) >= int(minSize) : # and int(fileSize) < int(maxSize) :
            count += 1
            countTotal += 1
            #print (path[0:100])
    
    if count > 0:
      print("{0:75} - {1:3}".format(myPath , count))

  print("TOTAL = " + str(countTotal))


def printDecadesStatistics(folderName):
  print("------------------------------------------")
  print("------", folderName, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

  decadeCount = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  
  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") != -1:
      (searchMovieName, year) = fileOperations.getNameYearFromNameWithIMDB(movieFolderName)

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
