﻿from re import search
from sys import orig_argv
from imdb import Cinemagoer

import time
import random
import os

#"F:\\FILMOVI\\_Al Pacino", \
#"F:\\FILMOVI\\_Clint Eastwood"
#"F:\\FILMOVI\\_Jack Nicholson",         \
#"F:\\FILMOVI\\_Jason Statham",       \
#"F:\\FILMOVI\\_John Wayne",       \
#"F:\\FILMOVI\\_Mel Gibson",       \
#"F:\\FILMOVI\\_Robert De Niro",       \
#"F:\\FILMOVI\\_Tom Hanks",       \
#"F:\\FILMOVI\\__Alien Anthology 1-4 (1979-1997)",       \
#"F:\\FILMOVI\\__Back to the Future",       \
#"F:\\FILMOVI\\__Batman",       \
#"F:\\FILMOVI\\__Before Sunrise-Sunset-Midnight Trilogy 1995-2013 720p x264 aac jbr",       \
#"F:\\FILMOVI\\__Beverly Hills Cop",       \
#"F:\\FILMOVI\\__Bourne",       \
#"F:\\FILMOVI\\__Conan",       \
#"F:\\FILMOVI\\__Die Hard 1-5 (1988-20013)",       \
#"F:\\FILMOVI\\__Dirty Harry Collection (1971-1988) 1080p Bluray.x264.anoXmous",       \
#"F:\\FILMOVI\\__Expendables",       \
#"F:\\FILMOVI\\__Fast and Furious 1-7 (2001-2015)",       \
#"F:\\FILMOVI\\__Godfather Trilogy 1972-1990",       \
#"F:\\FILMOVI\\__Godzilla",       \
#"F:\\FILMOVI\\__Gremlins.Duology.1984-1990.1080p.BluRay.DTS.x264-ETRG",       \
#"F:\\FILMOVI\\__Guardians of the Galaxy",       \
#"F:\\FILMOVI\\__Harry Potter Collection Box Set (1-8) (2001-2011)",       \
#"F:\\FILMOVI\\__Hobbit",       \
#"F:\\FILMOVI\\__Hunger games",       \
#"F:\\FILMOVI\\__Indiana Jones Quadrilogy  1-4 (1981-2008)",       \
#"F:\\FILMOVI\\__Iron man",       \
#"F:\\FILMOVI\\__James Bond Collection 1962 - 2015",       \
#"F:\\FILMOVI\\__John Wick",       \
#"F:\\FILMOVI\\__Jurassic Park",       \
#"F:\\FILMOVI\\__Lethal Weapon",       \
#"F:\\FILMOVI\\__Lord of the Rings Trilogy BluRay Extended 1080p QEBS5 AAC51 PS3 MP4-FASM",       \
#"F:\\FILMOVI\\__Mad Max",       \
#"F:\\FILMOVI\\__Man in black",       \
#"F:\\FILMOVI\\__Marvel - Avengers, Hulk, Thor, Capt America, Spiderman, Ant-man",       \
#"F:\\FILMOVI\\__Matrix Trilogy",       \
#"F:\\FILMOVI\\__Mission Impossible",       \
#"F:\\FILMOVI\\__Monty Python",       \
#"F:\\FILMOVI\\__Olympus, London, Angel has Fallen Trilogy",       \
#"F:\\FILMOVI\\__Pirates of The Caribbean 1-5 (2003-2017)",       \
#"F:\\FILMOVI\\__Planet of the Apes",       \
#"F:\\FILMOVI\\__Predator",       \
#"F:\\FILMOVI\\__Predator Quadrilogy BRRip 720p H264-3Li",       \
#"F:\\FILMOVI\\__Rambo",       \
#"F:\\FILMOVI\\__Resident evil, Underworld",       \
#"F:\\FILMOVI\\__Rocky",       \
#"F:\\FILMOVI\\__Star Trek",       \
#"F:\\FILMOVI\\__Star Wars",       \
#"F:\\FILMOVI\\__Superman",       \
#"F:\\FILMOVI\\__Taken",       \
#"F:\\FILMOVI\\__Terminator 1-6 (1984-2019)",       \
#"F:\\FILMOVI\\__Transformers 1-5",       \
#"F:\\FILMOVI\\__Transporter series",       \
#"F:\\FILMOVI\\__X-men",       \
#"F:\\FILMOVI\\___1930-60",       \
#"F:\\FILMOVI\\___1970's",       \
#"F:\\FILMOVI\\___1980's",       \
#"F:\\FILMOVI\\___1990's",       \
foldersToAnalyze = [ "F:\\FILMOVI\\___2000's",       \
  "F:\\FILMOVI\\___2010's",       \
"F:\\FILMOVI\\___2020's",       \
#"F:\\FILMOVI\\___CLASSICS",       \
#"F:\\FILMOVI\\___DOMACI",       \
#"F:\\FILMOVI\\___HITCHCOCK",       \
#"F:\\FILMOVI\\___HORROS",       \
#"F:\\FILMOVI\\___Japan movies",       \
#"F:\\FILMOVI\\___WAR MOVIES",       \
#"F:\\FILMOVI\\___WESTERNS",       \
]  

# A class is defined using the class statement.The body of a class contains a series of statements that execute during class definition
class MovieData(object):
    def __init__(self,name):        # poziva se kod inicijalizacije
        self.name = name
        self.movieID = 0
        self.year = 0
        self.runtime = 0
        self.rating = 0.0
        self.directors = ""
        self.genres = ""
        self.cast = ""
        self.plot = ""

# create an instance of the Cinemagoer class
ia = Cinemagoer()

#fetchMovieData(searchMovieName, releaseYear)
def fetchMovieData(searchMovieName, releaseYear):
  movie_data = MovieData(searchMovieName)

  searchMovieName = searchMovieName.rstrip()

  # TODO kad internet zakaže
  foundMoviesList = ia.search_movie(searchMovieName)
  if len(foundMoviesList) == 0 :
    movie_data.name = ""
    print ("SEARCH RETURNED NOTHING!!!\n")
    return movie_data

  movieID = foundMoviesList[0].movieID
  movieFound = False
  for m in foundMoviesList:
    try:
      t = m.data.get('title')
      y = m.data.get('year')
      if t == searchMovieName and y == releaseYear:
        movieID = m.movieID
        movieFound = True
        break
    except:
      print("OUCH")
  
  if movieFound == False:
    for movie in foundMoviesList:
      print("-- {0:15} -- {1:30}, {2}".format(movie.movieID, movie.data.get('title'), movie.data.get('year')))

  movie = ia.get_movie(movieID)

  movie_data.movieID = movieID

  try:
    rating = movie.data.get('rating', None)
    movie_data.rating = rating
    print("IMDB rating {0}".format(rating))

    year = movie.data.get('year', None)
    movie_data.year = year
    print("Year: {0}".format(year))

    runtime = int(movie.data['runtimes'][0])
    movie_data.runtime = runtime
    print("Runtime: ", runtime, " min")

    directors = ""
    cntDir = 0
    movieDirectors = movie.data.get('director', None)
    if movieDirectors != None:
      for director in movieDirectors:
          if cntDir > 0 :
            directors += ", "
          directors += director['name']
          cntDir += 1
    else:
      directors = " Problem with directors!!! "
    movie_data.directors = directors
    print("Directors: " + directors)

    genres = ""
    shortGenres = ""
    cntGen = 0
    for gen in movie.data['genres']:
      genres += gen + ", "
      if cntGen > 0 and cntGen <3 :
        shortGenres += ","
      if cntGen < 3:
        shortGenres += gen

      cntGen += 1
    movie_data.genres = genres
    print('Genres: ' + genres)

    cast = ""
    shortCast = "CAST - "
    for i in range(0,5):
      s = movie.data['cast'][i]
      cast += s.data['name']
      cast += ", "
      if i > 0 and i < 5 :
        shortCast += ","
      if i < 4 :
        shortCast += s.data['name']
              
    print('Cast: ' + cast)
    movie_data.cast = cast
        
    print ()
    plot = movie.data.get('plot outline', None)
    movie_data.plot = plot
    #print("Plot outline: " + str(plot))

  except:
    print("\nERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!\n")
    movie_data.name = ""

  return movie_data
    

def getMovieFolderNameFromMovieData(movie_data : MovieData):
  prefix = ""
  if movie_data.rating >= 9.0:
    prefix = "___"
  elif movie_data.rating >= 8.0:
    prefix = "__"
  elif movie_data.rating >= 7.0:
    prefix = "_"
  elif movie_data.rating < 6.0:
    prefix = "zzz_"
  
  newDirName = prefix + movie_data.name + " (" + str(movie_data.year) + ")" + " IMDB-" + str(movie_data.rating) + " " + movie_data.genres + " CAST - " + movie_data.cast
  
  return newDirName

def saveTXTWithMovieData(movie_data : MovieData, folderWhereItIs, movieFolderName):
  # formirati TXT datoteku s podacima
  fileName = folderWhereItIs + "\\" + movieFolderName + "\\" + "Film data - " + movie_data.name + " (" + str(movie_data.year) + ")" + ".txt"

  fileFilmData = open(fileName, 'w')
  fileFilmData.write(movie_data.name + "(" + str(movie_data.year) + ")\n")
  fileFilmData.write("MovieID:   " + str(movie_data.movieID) + "\n")
  fileFilmData.write("Runtime:   " + str(movie_data.runtime) + " min\n")
  fileFilmData.write("Genres:    " + movie_data.genres + "\n")
  fileFilmData.write("Directors: " + movie_data.directors + "\n")
  fileFilmData.write("Cast:      " + movie_data.cast + "\n")
  fileFilmData.write("Plot:      " + str(movie_data.plot))

  fileFilmData.close()
    
def saveMovieDataAndRenameFolder(movie_data : MovieData, folderWhereItIs, movieFolderName):

    # ime novog direktorija
    # Naziv (2022) IMDB-7.5 Adventure,Comedy,Thriller Cast-Mel Gibson, Jim Belushi, Joan Crawford
    newDirName = getMovieFolderNameFromMovieData(movie_data)   # movie_data.name + "(" + str(movie_data.year) + ")" + " IMDB-" + str(movie_data.rating) + " " + movie_data.genres + " CAST - " + movie_data.cast

    print("NEWDIR = ", newDirName)
    print ()

    # formirati TXT datoteku s podacima
    saveTXTWithMovieData(movie_data, folderWhereItIs, movieFolderName)

    # i sad idemo preimenovati direktorij
    origDir = folderWhereItIs + "\\" + movieFolderName
    destDir = folderWhereItIs + "\\" + newDirName

    # TODO provjeriti da li već postoji dest dir
    print("RENAMING - ", origDir, "   -   ", destDir)
    os.rename(origDir, destDir)

def processFolder(folderName):
  print("------------------------------------------")
  print("------", folderName, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

  fileErrors = open(folderName + "\\FileErrors.txt",'w', encoding="utf-8") 

  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") == -1:
      (searchMovieName, year) = getMovieNameFromFolder(movieFolderName)

      movie_data = fetchMovieData(searchMovieName, year)
    
      if movie_data.name != "":
        saveMovieDataAndRenameFolder(movie_data,folderName,movieFolderName)
 

def getMovieNameFromFolder(movieFolderName):
  earchMovieName = ""
  # provjeriti ima li točaka u nazivu
  parts = movieFolderName.split('.')

  # naći prvi string koji je kredibilna godina proizvodnje (1930 - 2022)
  cntParts=0
  year = 0
  searchMovieName = ""
  for part in parts:
    cntParts += 1
    # prvoga bi trebalo preskočiti (za filmove koji imaju broj u nazivu: 300, 1917, 2012)
    if cntParts == 1:
      continue
    
    if( part.isnumeric() ):
      year = int(part)
      if year > 1930 and year < 2023 :
        #nasli smo ga
        diskMovieName = ""
        searchMovieName = ""
        for piece in parts:
          if piece != part:
            diskMovieName += piece + " "
          else :
            # riješiti ukoliko ima _ na početku, da search name bude cist
            searchMovieName = diskMovieName.strip('_')

            # na diskMovieName cemo dodati i godinu
            diskMovieName += "(" + piece + ")"
            break
        
        print (diskMovieName, " - ", searchMovieName, " - ", movieFolderName)
  
  return (searchMovieName, year)

def folderStatistics(folderName):
  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]
  
  cntNotDone = 0
  cntImdb8 = 0
  cntImdb7 = 0
  cntImdbLower6 = 0

  listNotDone = []
  listWithoutMovieID = []

  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") != -1:
      ind = movieFolderName.find("IMDB")
      imdb_rat = movieFolderName[ind+5:ind+8]
      
      ind1 = movieFolderName.find("(")
      ind2 = movieFolderName.find(")")
      
      imdb_name = movieFolderName[0:ind1-1].strip("_")
      year_str  = movieFolderName[ind1+1:ind2]

      if float(imdb_rat) >= 8.0:
        cntImdb8 = cntImdb8 + 1
      elif float(imdb_rat) >= 7.0:
        cntImdb7 = cntImdb7 + 1
      elif float(imdb_rat) < 6.0:
        cntImdbLower6 = cntImdbLower6 + 1

      if doesFilmDataHasMovieID(folderName, movieFolderName, imdb_name, int(year_str)) == False:
        listWithoutMovieID.append(movieFolderName)
    else:
      cntNotDone = cntNotDone + 1
      listNotDone.append(movieFolderName)

  if cntNotDone == 0:
    return

  print("-- {0:65} -- {1:2}, {2:2}, {3:3}, {4:2}, {5:2}, {6:2}".format(folderName, cntNotDone, cntImdb8, cntImdb7, cntImdbLower6, len(listNotDone), len(listWithoutMovieID)))
  
  if len(listNotDone) > 0:
    print("LIST NOT DONE:")
    for movie in listNotDone: 
      print ("  ", movie)

  #if len(listWithoutMovieID) > 0:
  #  print("LIST WITHOUT MOVIE ID:")
  #  for movie in listWithoutMovieID:
  #    print ("  ", movie)

def rootFolderStatistics(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  for folderName in rootSubFolders:
    folderStatistics(folderName)
  
def doesFilmDataHasMovieID(folderWhereItIs, movieFolderName, movieName, movieYear):
  fileName = folderWhereItIs + "\\" + movieFolderName + "\\" + "Film data - " + movieName + " (" + str(movieYear) + ")" + ".txt"

  try:
    fileFilmData = open(fileName, 'r')
  except:
    return False

  if fileFilmData:
    first = fileFilmData.readline()
    second = fileFilmData.readline()
    
    if second.startswith("MovieID:"):
      return True

  return False


def folderRecheckDataWithIMDB(folderName):
  print("------", folderName, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]

  for movieFolderName in movieSubFolders:
    if movieFolderName.find("IMDB") != -1:
      ind1 = movieFolderName.find("(")
      ind2 = movieFolderName.find(")")
      imdb_name = movieFolderName[0:ind1-1].strip("_")
      year_str  = movieFolderName[ind1+1:ind2]
      
      # TODO - provjeriti ima li movieID,ako ima, onda nista
      if doesFilmDataHasMovieID(folderName, movieFolderName, imdb_name, int(year_str)) :
        continue

      print("-----------------------------------------------------")
      print("\nReal movie name: " + imdb_name)
      print("Year           : " + year_str)
      movie_data = fetchMovieData(imdb_name, int(year_str))

      if movie_data.name == "":
        print("SLEEPING 10-15 seconds :(((((")
        time.sleep(10 + random.randrange(0,5))
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

          # TODO provjeriti da li već postoji dest dir
          print("RENAMING - ", origDir, destDir)
          os.rename(origDir, destDir)

        time.sleep(10 + random.randrange(0,5))


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
  

#TODO
# proći kroz sve IMDB, i provjeriti da li se naziv direktorija slaže, s onim kako bi sada bilo
# provjeriti da li postoji movieID
# DONE - statistika - koji se sve ne slažu underscore s ocjenom

#folderStatistics("Z:\Movies\FILMOVI\___1970's")

#rootFolderUnderscoreStatistics("Z:\Movies\FILMOVI")
#folderReapplyUnderscoreRating("Z:\Movies\FILMOVI\___HITCHCOCK")

#folderRecheckDataWithIMDB("Z:\Movies\FILMOVI\___1930-60")

#rootFolderStatistics("Z:\Movies\FILMOVI")
processFolder("Z:\Movies\FILMOVI\___1970's")

#for folderName in foldersToAnalyze:
#  print(folderName)
#  folder = folderName
  #reapplyUnderscoreRating(folderName)
  #analyzeFolder(folderName)

#analyzeFolder(folder)