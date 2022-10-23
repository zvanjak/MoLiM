from datetime import date

import os


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
