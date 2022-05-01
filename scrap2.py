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
    for i in range(0,9):
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
    newDirName = realMovieName + " IMDB-" + str(rating) + " " + shortGenres + " " + shortCast

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

         
# get all movies in given dir
#   i godinu dohvatiti, za selekciju ako ima više filmova
#  npr. testirati s Love, 
#folder = "D:\Downloads"
#folder = "D:\Downloads\_Problematic"
#folder = "F:\FILMOVI\___1930-60"
#folder = "F:\\FILMOVI\\Novi_filmovi"
folder = "D:\To Watch\Filmovi"
#rootFolder = "F:\FILMOVI"

#rootSubFolders = [ f.path for f in os.scandir(rootFolder) if f.is_dir() ]

#for folder in rootSubFolders:
# u for petlji za sve filmove dovuci što se može iz IMDBa

# i onda nek korisnik odluči
