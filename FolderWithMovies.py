from datetime import date

import os

import fileOperations 
import IMDBMovieData 


class FolderWithMovies(object):
  def __init__(self, folderName):
    self.name = folderName
    self.movies = []                # list of MovieData

  def loadData(self):
    movieSubFolders = [ f.name for f in os.scandir(self.name) if f.is_dir() ]

    for movieFolderName in movieSubFolders:
      if movieFolderName.find("IMDB") != -1:
        (imdb_name, year_str) = fileOperations.getNameYearFromNameWithIMDB(movieFolderName)
      
        if fileOperations.doesFilmDataHasMovieID(self.name, movieFolderName, imdb_name, int(year_str)) == True :
          movie_data = fileOperations.loadIMDBMovieDataFromFilmData(self.name, movieFolderName, imdb_name, int(year_str))

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
  