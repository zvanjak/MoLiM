import time
import random
import os

import IMDBMovieData
import fileOperations 
import imdbAccess
import FolderWithMovies
import RootFolder 
import myFolders 
import processing 
import statistics 
import reports


def printDirectorsStatistics():
  root = RootFolder.RootFolder("Directors")

  root.loadDataFromListOfFolders( myFolders.actorsFolders + \
                                  myFolders.genresFolders + \
                                  myFolders.decadesFolders + \
                                  myFolders.directorsFolders + \
                                  myFolders.getSeriesFolderNames() + \
                                  ["E:\DONE", "Z:\Movies\FILMOVI\_____GOOD DONE"])

  tuplesList = []

  listDirectors = myFolders.getMiscDirectorsList() + myFolders.directorsList
  listDirectors.sort()
  
  for director in listDirectors:
    listMovies = root.getMoviesWithRatingHigherThanWithGivenDirector(5.0, director)
    listMovies.sort(key=lambda x: x.rating, reverse=True)
    if len(listMovies) > 0:
      sum = 0.0
      for movie in listMovies[0:10]:      # 10 best movies
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
    IMDBMovieData.printMoviesList(listMovies[0:10])
    print("AVG = ", tup[1])

def printActorsStatistics():
  root = RootFolder.RootFolder("Other actors")
  seriesFolders = myFolders.getSeriesFolderNames()
  listActors = myFolders.getMiscActorsList() + myFolders.actorsList
  listActors.sort()
  root.loadDataFromListOfFolders(myFolders.actorsFolders + myFolders.genresFolders + myFolders.decadesFolders + myFolders.directorsFolders + ["E:\DONE", "Z:\Movies\FILMOVI\_____GOOD DONE"] + seriesFolders) 

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
    IMDBMovieData.printMoviesList(listMovies[0:10])
    print("AVG = ", tup[1])


def printAllActorsMovies():
  root = RootFolder.RootFolder("Other actors")
  seriesFolders = myFolders.getSeriesFolderNames()
  listActors = myFolders.actorsList #+ myFolders.getMiscActorsList()
  listActors.sort()
  root.loadDataFromListOfFolders(myFolders.actorsFolders + myFolders.genresFolders + myFolders.decadesFolders + myFolders.directorsFolders + ["E:\DONE", "Z:\Movies\FILMOVI\_____GOOD DONE"] + seriesFolders) 

  tuplesList = []

  for actor in listActors:
    listMovies = root.getMoviesWithRatingHigherThanWithGivenActor(5.0, actor)
    listMovies.sort(key=lambda x: x.rating, reverse=True)
    if len(listMovies) > 0:
      sum = 0.0
      for movie in listMovies:
        sum += movie.rating
      newTuple = (actor, sum / len(listMovies) )
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
    IMDBMovieData.printMoviesList(listMovies)
    print("AVG = ", tup[1])


#statistics.folderStatistics("Z:\Movies\FILMOVI\_1970's")
#statistics.rootFolderStatistics("Z:\Movies\FILMOVI")

#statistics.folderSizeStatistic("Z:\Movies\FILMOVI\_1970's")
#statistics.printBigFiles()

#statistics.printDecadesStatistics("Z:\Movies\FILMOVI\_1970's")
#statistics.printRootDecadesStatistics("Z:\Movies\FILMOVI")

#printActorsStatistics()
#printDirectorsStatistics()
#printAllActorsMovies()


#processing.processSeriesFolder("F:\_OBRADITI")

processing.processFolder(r"D:\NEW MOVIES")

#processing.processListOfFolders( ( "Z:\Movies\FILMOVI\_____GOOD DONE\Denis Vilenueve",      \
#                                   "Z:\Movies\FILMOVI\_____GOOD DONE\Humphrey Bogart",      \
#                                   "Z:\Movies\FILMOVI\_____GOOD DONE\Jodie Foster",         \
#                                   "Z:\Movies\FILMOVI\_____GOOD DONE\Jodie Foster") )

#processing.folderRecheckDataWithIMDB("Z:\Movies\FILMOVI\_1970's")
#processing.rootFolderRecheckDataWithIMDB("Z:\Movies\FILMOVI")
#processing.reprocessFolderIMDBData("Z:\Movies\FILMOVI\____Romance")

#processing.copyDirectors(genresFolders)


#reports.rootFolderReportNoIMDBData("E:\\NEW MOVIES")
#reports.rootFolderReportNotDone("Z:\Movies\FILMOVI")


#movie = imdbAccess.fetchMovieDataByMovieID("Good Will Hunting", "0119217")


#seriesFolders = getSeriesFolderNames()
#root = RootFolder("Test series")
#root.loadDataFromListOfFolders(seriesFolders) 
#root.printMoviesWithRatingHigherThanWithGivenGenre(7.0, "Romance")
#root.printMoviesWithRatingHigherThanWithGivenDirector(5.0, "Ridley Scott")

#for director in directorsList:
#  root.printMoviesWithRatingHigherThanWithGivenDirector(5.0, director)
