from imdb import Cinemagoer

import os

# create an instance of the Cinemagoer class
ia = Cinemagoer()

# get all movies in given dir
#   i godinu dohvatiti, za selekciju ako ima više filmova
#  npr. testirati s Love, 
folder = "F:\FILMOVI\___1930-60"

subfolders = [ f.name for f in os.scandir(folder) if f.is_dir() ]

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
        for piece in parts:
          if piece != part:
            realMovieName += piece + " "
          else :
            realMovieName += "(" + piece + ")"
            break
        
        print (realMovieName)
        findMovie = ia.search_movie(realMovieName)
        movie = ia.get_movie(findMovie[0].movieID)

        rat = movie.data['rating']
        print("IMDB rating {0}".format(rat))

        runtime = int(movie.data['runtimes'][0])
        print("Runtime: {0}", runtime)

        directors = ""
        cntDir = 0
        for director in movie['directors']:
            if cntDir > 0 :
              directors += ", "
            directors += director['name']
            cntDir += 1
        print("Directors: " + directors)

        genres = ""
        for gen in movie.data['genres']:
          genres += gen + ", "
        print('Genres: ' + genres)

        cast = ""
        for i in range(1,10):
          s = movie.data['cast'][i]
          cast += s.data['name']
          cast += ", "
        print('Cast: ' + cast)
        
        plot = movie.data['plot outline']
        print(plot)



        a = 53
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