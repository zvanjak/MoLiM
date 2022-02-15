from imdb import Cinemagoer

import os

# create an instance of the Cinemagoer class
ia = Cinemagoer()

# get all movies in given dir
#   i godinu dohvatiti, za selekciju ako ima više filmova
#  npr. testirati s Love, 
#folder = "D:\Downloads"
folder = "D:\Downloads\_Problematic"
#folder = "F:\FILMOVI\___1930-60"
#folder = "F:\\FILMOVI\\Novi_filmovi"

subfolders = [ f.name for f in os.scandir(folder) if f.is_dir() ]

fileErrors = open("D:\Downloads\FileErrors.txt",'w') 

for movieName in subfolders:
  # provjeriti da li ima točku, ako nema ne diramo to -> provjerimo da li unutra ima nekih filmova!
  
  parts = movieName.split('.')

  # naći prvi string koji je kredibilna godina proizvodnje (1930 - 2022)
  for part in parts:
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
          for director in movie['directors']:
              if cntDir > 0 :
                directors += ", "
              directors += director['name']
              cntDir += 1
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
          #plot = movie.data.get('plot outline', None)
          #print("Plot outline: " + str(plot))

          # ime novog direktorija
          # Naziv (2022) IMDB-7.5 Adventure,Comedy,Thriller Cast-Mel Gibson, Jim Belushi, Joan Crawford
          newDirName = realMovieName
          newDirName += " IMDB-" + str(rating) + " " + shortGenres + " " + shortCast

          print("NEWDIR = ",newDirName)
          print ()

          # formirati TXT datoteku s podacima
          fileName = folder + "\\" + movieName + "\\" + "Film data - " + realMovieName + ".txt"
          fileFilmData = open(fileName, 'w')
          fileFilmData.write(str(realMovieName).strip('_') + "\n")
          # Name (Year)
          # Runtime
          # Genres
          # Directors
          # Cast
          # snimiti je u direktorij
          fileFilmData.close()
        except:
          print("ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!\n")

          # zapisati u datoteku 
          fileErrors.write(realMovieName + '\n')
          fileErrors.write(movieName + "\n")
          fileErrors.write("\n")

          fileErrors.flush()
        break


# EXCEPTION HANDLING ZA SVAKI PRISTUP PODACIMA
# NAPRAVITI FILE, U KOJI ĆE SE PREPISATI REZULTATI ANALIZE ZA SVAKI FAJL
# U STVARI, ZAPISATI SAMO ONE PROBLEMATIČNE, I ŠTO IM JE FALILO

# u for petlji za sve filmove dovuci što se može iz IMDBa

# i onda nek korisnik odluči

# get a movie
movie = ia.get_movie('0133093')

# print the names of the directors of the movie
#print('Directors:')
#for director in movie['directors']:
#    print(director['name'])

## print the genres of the movie
#print('Genres:')
#for genre in movie['genres']:
#    print(genre)

## search for a person name
#people = ia.search_person('Mel Gibson')
#for person in people:
#   print(person.personID, person['name'])