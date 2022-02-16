from imdb import Cinemagoer

import os

# create an instance of the Cinemagoer class
ia = Cinemagoer()

# get all movies in given dir
#   i godinu dohvatiti, za selekciju ako ima više filmova
#  npr. testirati s Love, 
#folder = "D:\Downloads"
#folder = "D:\Downloads\_Problematic"
#folder = "F:\FILMOVI\___1980's"
folder = "F:\\FILMOVI\\Novi_filmovi"

subfolders = [ f.name for f in os.scandir(folder) if f.is_dir() ]

fileErrors = open(folder + "\\FileErrors.txt",'w', encoding="utf-8") 

for movieName in subfolders:
  # provjeriti da li ima točku, ako nema ne diramo to -> provjerimo da li unutra ima nekih filmova!
  if movieName.count('.') < 2:
    if movieName.find("IMDB") != -1:
      print("\nDONE: " + movieName)
      continue

    # ako nema točku, i NISMO ga već obradili, onda ćemo probati split po spaceu ' '
    parts = movieName.split(' ')

    #print("\nSKIPPING: " + movieName)
    fileErrors.write("\nTRYING SPACES - " + str(movieName) + "\n\n")

  else:
    parts = movieName.split('.')

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
        print (movieName)
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
        
        print (realMovieName)

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
          for i in range(1,10):
            s = movie.data['cast'][i]
            cast += s.data['name']
            cast += ", "
            if i > 1 and i <= 3 :
              shortCast += ","
            if i <= 3 :
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
        break


# u for petlji za sve filmove dovuci što se može iz IMDBa

# i onda nek korisnik odluči
