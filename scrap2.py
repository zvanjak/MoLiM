﻿from sys import orig_argv
from imdb import Cinemagoer

import os

# create an instance of the Cinemagoer class
ia = Cinemagoer()

def fetchMovieDataPerformRenameSaveText(movieName, realMovieName, searchMovieName):
  try:
    findMovie = ia.search_movie(searchMovieName)
    ind = 0
    #movieID1 = findMovie[0].movieID
    #movieID2 = findMovie[1].movieID
    #if int(movieID2) < int(movieID1) :
    #  ind = 1
    movie = ia.get_movie(findMovie[ind].movieID)

    rating = movie.data.get('rating', None)
    print("IMDB rating {0}".format(rating))

    year = movie.data.get('year', None)
    print("Year: {0}".format(year))

    runtime = int(movie.data['runtimes'][0])
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
      print("Directors: " + directors)
    else:
      fileErrors.write("\n" + realMovieName + " Problem with directors!!! " + "\n")

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
    print('Genres: ' + genres)

    cast = ""
    shortCast = "CAST - "
    for i in range(0,4):
      s = movie.data['cast'][i]
      cast += s.data['name']
      cast += ", "
      if i > 0 and i < 3 :
        shortCast += ","
      if i < 3 :
        shortCast += s.data['name']
              
    print('Cast: ' + cast)
        
    print ()
    plot = movie.data.get('plot outline', None)
    #print("Plot outline: " + str(plot))

    # ime novog direktorija
    # Naziv (2022) IMDB-7.5 Adventure,Comedy,Thriller Cast-Mel Gibson, Jim Belushi, Joan Crawford
    newDirName = searchMovieName + "(" + str(year) + ")" + " IMDB-" + str(rating) + " " + shortGenres + " " + shortCast

    if rating > 8.0:
      newDirName = "__" + newDirName
    elif rating > 7.0:
      newDirName = "_" + newDirName

    print("NEWDIR = ",newDirName)
    print ()

    # formirati TXT datoteku s podacima
    fileName = folder + "\\" + movieName + "\\" + "Film data - " + realMovieName + ".txt"

    fileFilmData = open(fileName, 'w')
    fileFilmData.write(str(realMovieName).strip('_') + "\n")
    fileFilmData.write("Runtime:   " + str(runtime) + " min\n")
    fileFilmData.write("Genres:    " + genres + "\n")
    fileFilmData.write("Directors: " + directors + "\n")
    fileFilmData.write("Cast:      " + cast + "\n")
    fileFilmData.write("Plot:      " + str(plot))

    fileFilmData.close()

    # i sad idemo preimenovati direktorij
    origDir = folder + "\\" + movieName
    destDir = folder + "\\" + newDirName

    os.rename(origDir, destDir)

  except:
    print("\nERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!\n")
    
    origDir = folder + "\\" + movieName
    destDir = folder + "\\" + "___" + movieName
    print("RENAMING {0} to {1}", origDir, destDir)

    # i sad idemo preimenovati direktorij
    os.rename(origDir, destDir)

    # zapisati u datoteku 
    fileErrors.write(realMovieName + '\n')
    fileErrors.write(movieName + "\n")
    fileErrors.write("\n")

    fileErrors.flush()

def processFolder(folder):
  print("------------------------------------------")
  print("------", folder, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folder) if f.is_dir() ]

  fileErrors = open(folder + "\\FileErrors.txt",'w', encoding="utf-8") 

  for movieFileName in movieSubFolders:
    # provjeriti da li ima točku, ako nema ne diramo to -> provjerimo da li unutra ima nekih filmova!
    if movieFileName.count('.') < 2:
      if movieFileName.find("IMDB") != -1:
        # TODO treba popraviti cast :(
        #parPos = movieFileName.find('(')
        #searchMovieName = movieFileName[0:parPos-1].strip('_')
      
        #parPos = movieFileName.find(')')
        #realMovieName = movieFileName[0:parPos+1]

        #fetchMovieDataPerformRenameSaveText(movieFileName, realMovieName, searchMovieName)

        print("\nDONE: " + movieFileName)
        continue

      # ako nema točku, i NISMO ga već obradili, onda ćemo probati split po spaceu ' '
      parts = movieFileName.split(' ')

      #print("\nSKIPPING: " + movieName)
      fileErrors.write("\nTRYING SPACES - " + str(movieFileName) + "\n\n")

    else:
      parts = movieFileName.split('.')

    # naći prvi string koji je kredibilna godina proizvodnje (1930 - 2022)
    cntParts=0
    for part in parts:
      cntParts += 1
      # prvoga bi trebalo preskočiti
      if cntParts == 1:
        continue
    
      if( part.isnumeric() ):
        year = int(part)
        if year > 1930 and year < 2023 :
          #nasli smo ga
          realMovieName = ""
          searchMovieName = ""
          for piece in parts:
            if piece != part:
              realMovieName += piece + " "
            else :
              searchMovieName = realMovieName.strip('_')
              # riješiti ukoliko ima ___ na početku

              realMovieName += "(" + piece + ")"
              break
        
          print (realMovieName, " - ", movieFileName)

          fetchMovieDataPerformRenameSaveText(movieFileName, realMovieName, searchMovieName)

          break

def getMovieData(movieFileName):
  parts = movieFileName.split('.')

  # naći prvi string koji je kredibilna godina proizvodnje (1930 - 2022)
  cntParts=0
  for part in parts:
    cntParts += 1
    # prvoga bi trebalo preskočiti
    if cntParts == 1:
      continue
    
    if( part.isnumeric() ):
      year = int(part)
      if year > 1930 and year < 2023 :
        #nasli smo ga
        realMovieName = ""
        searchMovieName = ""
        for piece in parts:
          if piece != part:
            realMovieName += piece + " "
          else :
            searchMovieName = realMovieName.strip('_')
            # riješiti ukoliko ima ___ na početku

            realMovieName += "(" + piece + ")"
            break
        
        print (realMovieName, " - ", searchMovieName, " - ", movieFileName)

        fetchMovieDataPerformRenameSaveText(movieFileName, realMovieName, searchMovieName)

        break
  else:
    origDir = folder + "\\" + movieFileName
    destDir = folder + "\\" + "___" + movieFileName
    print("RENAMING {0} to {1}", origDir, destDir)

    os.rename(origDir, destDir)

def analyzeFolder(folder):
  print("------------------------------------------")
  print("------", folder, "------")
  print("------------------------------------------")

  movieSubFolders = [ f.name for f in os.scandir(folder) if f.is_dir() ]

  for movieFileName in movieSubFolders:
    if movieFileName.find("IMDB") != -1:
      ind = movieFileName.find("IMDB")
      imdb_rat = movieFileName[ind+5:ind+8]
      
      print(imdb_rat)
      
      if float(imdb_rat) >= 8.0:
        origDir = folder + "\\" + movieFileName
        destDir = folder + "\\" + "__" + movieFileName
        print("RENAMING {0} to {1}", origDir, destDir)
        os.rename(origDir, destDir)
      elif float(imdb_rat) >= 7.0:
        origDir = folder + "\\" + movieFileName
        destDir = folder + "\\" + "_" + movieFileName
        print("RENAMING {0} to {1}", origDir, destDir)
        os.rename(origDir, destDir)
      elif float(imdb_rat) < 6.0:
        origDir = folder + "\\" + movieFileName
        destDir = folder + "\\" + "zzz_" + movieFileName
        print("RENAMING {0} to {1}", origDir, destDir)
        os.rename(origDir, destDir)
      continue
    else:
      print("\nNOT DONE: " + movieFileName)
      getMovieData(movieFileName)


         
# get all movies in given dir
#   i godinu dohvatiti, za selekciju ako ima više filmova
#  npr. testirati s Love, 
#folder = "D:\Downloads"
#folder = "D:\Downloads\_Problematic"
#folder = "F:\FILMOVI\___1930-60"
#folder = "F:\\FILMOVI\\Novi_filmovi"
folder = "D:\To Watch\Filmovi"
#folder = "D:\To Watch\___TEST"
rootFolder = "F:\FILMOVI"
#foldersToAnalyze = [ "F:\\FILMOVI\\_Al Pacino", \
"F:\\FILMOVI\\_Clint Eastwood",       \
"F:\\FILMOVI\\_Jack Nicholson",       \
"F:\\FILMOVI\\_Jason Statham",       \
"F:\\FILMOVI\\_John Wayne",       \
"F:\\FILMOVI\\_Mel Gibson",       \
"F:\\FILMOVI\\_Robert De Niro",       \
"F:\\FILMOVI\\_Tom Hanks",       \
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
#"F:\\FILMOVI\\___2000's",       \
#"F:\\FILMOVI\\___2010's",       \
#"F:\\FILMOVI\\___2020's",       \
#"F:\\FILMOVI\\___CLASSICS",       \
#"F:\\FILMOVI\\___DOMACI",       \
#"F:\\FILMOVI\\___HITCHCOCK",       \
#"F:\\FILMOVI\\___HORROS",       \
#"F:\\FILMOVI\\___Japan movies",       \
#"F:\\FILMOVI\\___WAR MOVIES",       \
#"F:\\FILMOVI\\___WESTERNS",       \
]  

#rootSubFolders = [ f.path for f in os.scandir(rootFolder) if f.is_dir() ]

#for folderName in rootSubFolders:
#  print("\"" + folderName + "\",       prdo" )

# i onda nek korisnik odluči
fileErrors = open(folder + "\\FileErrors.txt",'w', encoding="utf-8") 

for folderName in foldersToAnalyze:
  print(folderName)
  folder = folderName
  analyzeFolder(folderName)

#analyzeFolder(folder)