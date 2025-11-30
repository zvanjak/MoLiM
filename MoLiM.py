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
import movieStatistics 
import reports


def printDirectorsStatistics():
    root = RootFolder.RootFolder("Directors")

    root.loadDataFromListOfFolders(
        myFolders.actorsFolders +
        myFolders.genresFolders +
        myFolders.decadesFolders +
        myFolders.directorsFolders +
        myFolders.getSeriesFolderNames() +
        [r"E:\DONE", r"Z:\Movies\FILMOVI\_____GOOD DONE"]
    )

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
            newTuple = (director, sum / len(listMovies[0:10]))
            tuplesList.append(newTuple)
        else:
            print("     -----------------                   NO MOVIES FOR DIRECTOR - ", director)

    tuplesList.sort(key=lambda x: x[1], reverse=True)

    ordNum = 0
    for tup in tuplesList:
        director = tup[0]
        ordNum += 1
        print("-----------------------------------------------------------------")
        print("{0} - DIRECTOR - {1}".format(ordNum, director))
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
    root.loadDataFromListOfFolders(
        myFolders.actorsFolders +
        myFolders.genresFolders +
        myFolders.decadesFolders +
        myFolders.directorsFolders +
        [r"E:\DONE", r"Z:\Movies\FILMOVI\_____GOOD DONE"] +
        seriesFolders
    )

    tuplesList = []

    for actor in listActors:
        listMovies = root.getMoviesWithRatingHigherThanWithGivenActor(5.0, actor)
        listMovies.sort(key=lambda x: x.rating, reverse=True)
        if len(listMovies) > 0:
            sum = 0.0
            for movie in listMovies[0:10]:
                sum += movie.rating
            newTuple = (actor, sum / len(listMovies[0:10]))
            tuplesList.append(newTuple)
        else:
            print("     -----------------                   NO MOVIES FOR ACTOR - ", actor)

    tuplesList.sort(key=lambda x: x[1], reverse=True)

    ordNum = 0
    for tup in tuplesList:
        actor = tup[0]
        ordNum += 1
        print("-----------------------------------------------------------------")
        print("{0} - ACTOR - {1}".format(ordNum, actor))
        print("-----------------------------------------------------------------")

        listMovies = root.getMoviesWithRatingHigherThanWithGivenActor(5.0, actor)
        listMovies.sort(key=lambda x: x.rating, reverse=True)
        IMDBMovieData.printMoviesList(listMovies[0:10])
        print("AVG = ", tup[1])


def printAllActorsMovies():
    root = RootFolder.RootFolder("Other actors")
    seriesFolders = myFolders.getSeriesFolderNames()
    listActors = myFolders.actorsList  # + myFolders.getMiscActorsList()
    listActors.sort()
    root.loadDataFromListOfFolders(
        myFolders.actorsFolders +
        myFolders.genresFolders +
        myFolders.decadesFolders +
        myFolders.directorsFolders +
        [r"E:\DONE", r"Z:\Movies\FILMOVI\_____GOOD DONE"] +
        seriesFolders
    )

    tuplesList = []

    for actor in listActors:
        listMovies = root.getMoviesWithRatingHigherThanWithGivenActor(5.0, actor)
        listMovies.sort(key=lambda x: x.rating, reverse=True)
        if len(listMovies) > 0:
            sum = 0.0
            for movie in listMovies:
                sum += movie.rating
            newTuple = (actor, sum / len(listMovies))
            tuplesList.append(newTuple)
        else:
            print("     -----------------                   NO MOVIES FOR ACTOR - ", actor)

    tuplesList.sort(key=lambda x: x[1], reverse=True)

    ordNum = 0
    for tup in tuplesList:
        actor = tup[0]
        ordNum += 1
        print("-----------------------------------------------------------------")
        print("{0} - ACTOR - {1}".format(ordNum, actor))
        print("-----------------------------------------------------------------")

        listMovies = root.getMoviesWithRatingHigherThanWithGivenActor(5.0, actor)
        listMovies.sort(key=lambda x: x.rating, reverse=True)
        IMDBMovieData.printMoviesList(listMovies)
        print("AVG = ", tup[1])


# Entry point - currently processing new movies
if __name__ == "__main__":
    processing.processFolder(r"E:\NOVI FILMOVI")

# Commented out examples - kept for reference
# movieStatistics.folderStatistics(r"Z:\Movies\FILMOVI\_1970's")
# movieStatistics.rootFolderStatistics(r"Z:\Movies\FILMOVI")
# movieStatistics.folderSizeStatistic(r"Z:\Movies\FILMOVI\_1970's")
# movieStatistics.printBigFiles()
# movieStatistics.printDecadesStatistics(r"Z:\Movies\FILMOVI\_1970's")
# movieStatistics.printRootDecadesStatistics(r"Z:\Movies\FILMOVI")
# printActorsStatistics()
# printDirectorsStatistics()
# printAllActorsMovies()
# processing.processSeriesFolder(r"E:\NOVE SERIJE")
# reports.rootFolderReportNoIMDBData(r"E:\NEW MOVIES")
# reports.rootFolderReportNotDone(r"Z:\Movies\FILMOVI")
