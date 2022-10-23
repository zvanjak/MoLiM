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
        (imdb_name, year_str) = fileOperations.getNameYearFromNameWithIMDB(movieFolderName)

        if fileOperations.doesFilmDataHasMovieID(folderName, movieFolderName, imdb_name, int(year_str)) == False:
          listWithoutMovieID.append(movieFolderName)

    if len(listWithoutMovieID) == 0:
      continue

    print("-- {0:65} -- {1:2}".format(folderName, len(listWithoutMovieID)))
  
    if len(listWithoutMovieID) > 0:
      print("LIST WITHOUT MOVIE ID:")
      for movie in listWithoutMovieID:
        print ("  ", movie)

