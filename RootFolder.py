from datetime import date

import os

import IMDBMovieData 
import FolderWithMovies


class RootFolder(object):
  def __init__(self, rootFolderName : str):
    self.name = rootFolderName
    self.folders = []               # list of FolderWithMovies

  def loadData(self):
    rootSubFolders = [ f.path for f in os.scandir(self.name) if f.is_dir() ]

    for folderName in rootSubFolders:
      print("Adding - ", folderName)
      newFolder = FolderWithMovies.FolderWithMovies(folderName)
      newFolder.loadData()
      self.folders.append(newFolder)

  def loadDataFromListOfFolders(self, listFolders):
    for folderName in listFolders:
      print("Adding - ", folderName)
      newFolder = FolderWithMovies.FolderWithMovies(folderName)
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
        IMDBMovieData.printMoviesList(newMovies)

  def printMoviesWithRatingHigherThanWithGivenDirector(self, rating : float, director : str) :
    for folder in self.folders:
      newMovies = folder.getMoviesWithRatingHigherThanWithGivenDirector(rating, director)
      if len(newMovies) > 0 :
        print(folder.name)
        IMDBMovieData.printMoviesList(newMovies)

  def printMoviesWithRatingHigherThanWithGivenGenre(self, rating : float, genre : str) :
    for folder in self.folders:
      newMovies = folder.getMoviesWithRatingHigherThanWithGivenGenre(rating, genre)
      if len(newMovies) > 0 :
        print(folder.name)
        IMDBMovieData.printMoviesList(newMovies)

  def printMoviesWithRatingHigherThanWithGivenActor(self, rating : float, actor : str) :
    for folder in self.folders:
      newMovies = folder.getMoviesWithRatingHigherThanWithGivenActor(rating, actor)
      if len(newMovies) > 0 :
        print(folder.name)
        IMDBMovieData.printMoviesList(newMovies)
