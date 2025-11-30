from datetime import date

import os


otherActorsFolder = r"Z:\Movies\FILMOVI\___00_Actors_others"
otherDirectorsFolder = r"Z:\Movies\FILMOVI\__00_Directors_others"

directorsFolders = [
    r"Z:\Movies\FILMOVI\__Akira Kurosawa",
    r"Z:\Movies\FILMOVI\__Alfred Hitchcock",
    r"Z:\Movies\FILMOVI\__Christopher Nolan",
    r"Z:\Movies\FILMOVI\__Coen brothers",
    r"Z:\Movies\FILMOVI\__John Ford",
    r"Z:\Movies\FILMOVI\__Martin Scorsese",
    r"Z:\Movies\FILMOVI\__Quentin Tarantino",
    r"Z:\Movies\FILMOVI\__Ridley Scott",
    r"Z:\Movies\FILMOVI\__Stanley Kubrick",
    r"Z:\Movies\FILMOVI\__Steven Spielberg"
]

directorsList = [
    "Akira Kurosawa",
    "Alfred Hitchcock",
    "Christopher Nolan",
    "Coen",
    "John Ford",
    "Martin Scorsese",
    "Quentin Tarantino",
    "Ridley Scott",
    "Stanley Kubrick",
    "Steven Spielberg"
]

actorsFolders = [
    r"Z:\Movies\FILMOVI\___Al Pacino",
    r"Z:\Movies\FILMOVI\___Brad Pitt",
    r"Z:\Movies\FILMOVI\___Bruce Lee",
    r"Z:\Movies\FILMOVI\___Clint Eastwood",
    r"Z:\Movies\FILMOVI\___Humphrey Bogart",
    r"Z:\Movies\FILMOVI\___Jack Nicholson",
    r"Z:\Movies\FILMOVI\___John Wayne",
    r"Z:\Movies\FILMOVI\___Leonardo DiCaprio",
    r"Z:\Movies\FILMOVI\___Mel Gibson",
    r"Z:\Movies\FILMOVI\___Robert De Niro",
    r"Z:\Movies\FILMOVI\___Spencer Tracy",
    r"Z:\Movies\FILMOVI\___Tom Cruise",
    r"Z:\Movies\FILMOVI\___Tom Hanks"
]

actorsList = [
    "Al Pacino",
    "Brad Pitt",
    "Bruce Lee",
    "Clint Eastwood",
    "Humphrey Bogart",
    "Jack Nicholson",
    "John Wayne",
    "Leonardo DiCaprio",
    "Mel Gibson",
    "Robert De Niro",
    "Spencer Tracy",
    "Tom Cruise",
    "Tom Hanks",
]

genresFolders = [
    r"Z:\Movies\FILMOVI\____Action, Crime & Thriller",
    r"Z:\Movies\FILMOVI\____Adventure",
    r"Z:\Movies\FILMOVI\____Biography & History",
    r"Z:\Movies\FILMOVI\____Comedy",
    r"Z:\Movies\FILMOVI\____Drama",
    r"Z:\Movies\FILMOVI\____Europe & Asia movies",
    r"Z:\Movies\FILMOVI\____Family fun",
    r"Z:\Movies\FILMOVI\____Horrors",
    r"Z:\Movies\FILMOVI\____Romance",
    r"Z:\Movies\FILMOVI\____Science Fiction & Fantasy",
    r"Z:\Movies\FILMOVI\____War movies",
    r"Z:\Movies\FILMOVI\____Westerns"
]

decadesFolders = [
    r"Z:\Movies\FILMOVI\_1920-40's",
    r"Z:\Movies\FILMOVI\_1950's",
    r"Z:\Movies\FILMOVI\_1960's",
    r"Z:\Movies\FILMOVI\_1970's",
    r"Z:\Movies\FILMOVI\_1980's",
    r"Z:\Movies\FILMOVI\_1990's",
    r"Z:\Movies\FILMOVI\_2000's",
    r"Z:\Movies\FILMOVI\_2010's",
    r"Z:\Movies\FILMOVI\_2020's"
]


def getMiscDirectorsList():
    startFolder = otherDirectorsFolder
    listDirectors = [f.name for f in os.scandir(startFolder) if f.is_dir()]
    return listDirectors


def getMiscActorsList():
    startFolder = otherActorsFolder
    listActors = [f.name for f in os.scandir(startFolder) if f.is_dir()]
    return listActors


def getSeriesFolderNames():
    listNames = []
    startFolder = r"Z:\Movies\FILMOVI"
    subFolders = [f.name for f in os.scandir(startFolder) if f.is_dir()]

    for folderName in subFolders:
        if (folderName.startswith("_") and 
            not folderName.startswith("__") and 
            not folderName.startswith("___") and 
            not folderName.startswith("____")):
            if folderName[2] >= '0' and folderName[2] <= '9':
                continue
            else:
                listNames.append(os.path.join(startFolder, folderName))
                print(folderName)

    return listNames
