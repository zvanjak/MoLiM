from re import search
from shutil import move
from sys import orig_argv
from typing import Tuple
from xmlrpc.client import Boolean
from imdb import Cinemagoer

from datetime import date

import time
import random

import IMDBMovieData


# create an instance of the Cinemagoer class
ia = Cinemagoer()


# fetchMovieData(searchMovieName, releaseYear)
def fetchMovieData(searchMovieName, releaseYear) -> IMDBMovieData:
  movie_data = IMDBMovieData.IMDBMovieData(searchMovieName)

  searchMovieName = searchMovieName.rstrip()

  # TODO kad internet zaka�e
  try:
    foundMoviesList = ia.search_movie(searchMovieName)
  except:
    print("\n--------   EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET --------\n")
    time.sleep(30)
    movie_data.name = ""
    return movie_data

  if len(foundMoviesList) == 0 :
    movie_data.name = ""
    print ("\n   ----   SEARCH RETURNED NOTHING!!!   ----\n")
    time.sleep(20)
    return movie_data

  movieID = foundMoviesList[0].movieID
  movieFound = False
  for m in foundMoviesList:
    try:
      t = m.data.get('title')
      y = m.data.get('year')
      k = m.data.get('kind')
      if t == searchMovieName and y == releaseYear and k == 'movie':
        movieID = m.movieID
        movieFound = True
        break
    except:
      print("OUCH")
  
  if movieFound == False:
    print ("COULD NOT FIND EXACT MOVIE WITH NAME AND YEAR") 
    for movie in foundMoviesList:
      print("-- {0:15} -- {1:30}, {2}".format(movie.movieID, movie.data.get('title'), movie.data.get('year')))
    #movie_data.name = ""
    #return movie_data

  movie_data = fetchMovieDataByMovieID(searchMovieName, movieID)

  time.sleep(5+random.randrange(0,5))

  return movie_data

def fetchMovieDataByMovieID(name : str, movieID : str) -> IMDBMovieData.IMDBMovieData:
  movie_data = IMDBMovieData.IMDBMovieData(name)

  try:
     movie = ia.get_movie(movieID)
  except:
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    time.sleep(30)
    movie_data.name = ""
    return movie_data

  movie_data.movieID = movieID

  try:
    movie_data.imdb_name = movie.data.get('title')

    rating = movie.data.get('rating', None)
    movie_data.rating = rating
    print("IMDB rating:  {0}".format(rating))

    votes = movie.data.get('votes', 0)
    movie_data.votes = votes
    print("Num. votes:   {0}".format(votes))

    box_office_data = movie.data.get('box office', None)
    if box_office_data != None:
      movie_data.box_office = str(box_office_data)
      print("Box office:   {0}".format(box_office_data))

    release_date = movie.data.get('original air date', None)
    if release_date != None:
      movie_data.releaseDate = release_date
      print("Release date: {0}".format(release_date))

    year = movie.data.get('year', None)
    movie_data.year = year
    print("Year:         {0}".format(year))

    if 'runtimes' in movie.data:
      runtime = int(movie.data['runtimes'][0])
      movie_data.runtime = runtime
      print("Runtime:     ", runtime, " min")
    else:
      print("-------------------------------------------")
      print("NO RUNTIME!!!!")
      print("-------------------------------------------")
      movie_data.runtime = 0

    if 'top 250 rank' in movie.data:
      movie_data.top250rank = int(movie.data['top 250 rank'])

    if 'countries' in movie.data:
      movie_data.countries = str(movie.data['countries'])

    if 'languages' in movie.data:
      movie_data.languages = str(movie.data['languages'])

    directors = ""
    cntDir = 0
    if 'director' in movie.data:
      movieDirectors = movie.data.get('director')
      for director in movieDirectors:
          if cntDir > 0 :
            directors += ", "
          directors += director['name']
          cntDir += 1
    else:
      directors = " Problem with directors!!! "
    movie_data.directors = directors
    print("Directors:    " + directors)

    producers = ""
    cntProd = 0
    if 'producer' in movie.data:
      movieProducers = movie.data.get('producer')
      for producer in movieProducers:
          if cntProd > 0 :
            producers += ", "

          if 'name' in producer:
            producers += producer['name']
          cntProd += 1

          if cntProd > 5:
            break
    else:
      producers = " Problem with producers!!! "
    movie_data.producers = producers
    print("Producers:    " + producers)

    writers = ""
    cntWrit = 0
    if 'writer' in movie.data:
      movieWriters = movie.data.get('writer')
      for writer in movieWriters:
          if cntWrit > 0 :
            writers += ", "

          if 'name' in writer:
            writers += writer['name']
          cntWrit += 1
    else:
      writers = " Problem with writers!!! "
    movie_data.writers = writers
    print("Writers:      " + writers)

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
    print('Genres:       ' + genres)

    cast = ""
    shortCast = ""
    if 'cast' in movie.data:
      i = 0
      for actor in movie.data['cast']:
        cast += actor['name']
        cast += ", "
        if i < 5 :
          shortCast += actor['name']
        if i >= 0 and i < 4 :
          shortCast += ", "
        i = i + 1
              
      print('Cast:         ' + shortCast)
      movie_data.cast_complete = cast
      movie_data.cast_leads = shortCast
    else:
      print("-------------------------------------------")
      print("NO CAST!!!")
      print("-------------------------------------------")
        
    print ()
    plot = movie.data.get('plot outline', None)
    movie_data.plot = plot
    #print("Plot outline: " + str(plot))

  except:
    print("\nERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!\n")
    movie_data.name = ""
  
  return movie_data



# fetchSeriesData(searchMovieName)
def fetchSeriesData(searchMovieName):
  movie_data = IMDBMovieData.IMDBMovieData(searchMovieName)

  searchMovieName = searchMovieName.rstrip()

  # TODO kad internet zaka�e
  try:
    foundMoviesList = ia.search_movie(searchMovieName)
  except:
    print("\n--------   EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET --------\n")
    time.sleep(30)
    movie_data.name = ""
    return movie_data

  if len(foundMoviesList) == 0 :
    movie_data.name = ""
    print ("\n   ----   SEARCH RETURNED NOTHING!!!   ----\n")
    time.sleep(20)
    return movie_data

  movieID = foundMoviesList[0].movieID
  movieFound = False
  for m in foundMoviesList:
    try:
      t = m.data.get('title')
      k = m.data.get('kind')
      if t == searchMovieName and k == 'tv series':
        movieID = m.movieID
        movieFound = True
        break
    except:
      print("OUCH")
  
  if movieFound == False:
    print ("COULD NOT FIND EXACT MOVIE WITH NAME AND YEAR") 
    for movie in foundMoviesList:
      print("-- {0:15} -- {1:30}, {2}".format(movie.movieID, movie.data.get('title'), movie.data.get('year')))
    #movie_data.name = ""
    #return movie_data

  movie_data = fetchSeriesDataByMovieID(searchMovieName, movieID)

  time.sleep(5+random.randrange(0,5))

  return movie_data


def fetchSeriesDataByMovieID(name : str, movieID : str) -> IMDBMovieData.IMDBMovieData:
  series_data = IMDBMovieData.IMDBMovieData(name)

  try:
     series = ia.get_movie(movieID)

     ia.update(series, 'episodes')

     season_keys = sorted(series['episodes'].keys())

     num_seasons = len(series['episodes'].keys())
     print("Seasons num = {0}".format(num_seasons))

     for season_id in season_keys:
       print("Season {0}".format(season_id))
       season_data = series['episodes'][season_id]
       
       episode_num = len(season_data)
       print("Episode num = {0}".format(episode_num))
       
       for i in range(0,episode_num):
         episode = series['episodes'][season_id][i]
         print(episode['title'])
         print(episode.data['rating'])
         print(episode.data['votes'])
         print(episode.data['original air date'])
         print(episode.data['year'])
         print(episode.data['plot'])


  except:
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    time.sleep(30)
    series_data.name = ""
    return series_data

  series_data.movieID = movieID

  try:
    series_data.imdb_name = series.data.get('title')

    rating = series.data.get('rating', None)
    series_data.rating = rating
    print("IMDB rating:  {0}".format(rating))

    votes = series.data.get('votes', 0)
    series_data.votes = votes
    print("Num. votes:   {0}".format(votes))

    year = series.data.get('year', None)
    series_data.year = year
    print("Year:         {0}".format(year))

    if 'runtimes' in series.data:
      runtime = int(series.data['runtimes'][0])
      series_data.runtime = runtime
      print("Runtime:     ", runtime, " min")
    else:
      print("-------------------------------------------")
      print("NO RUNTIME!!!!")
      print("-------------------------------------------")
      series_data.runtime = 0

    if 'countries' in series.data:
      series_data.countries = str(series.data['countries'])

    if 'languages' in series.data:
      series_data.languages = str(series.data['languages'])
      
    writers = ""
    cntWrit = 0
    if 'writer' in series.data:
      movieWriters = series.data.get('writer')
      for writer in movieWriters:
          if cntWrit > 0 :
            writers += ", "

          if 'name' in writer:
            writers += writer['name']
          cntWrit += 1
    else:
      writers = " Problem with writers!!! "
    series_data.writers = writers
    print("Writers:      " + writers)

    genres = ""
    shortGenres = ""
    cntGen = 0
    for gen in series.data['genres']:
      genres += gen + ", "
      if cntGen > 0 and cntGen <3 :
        shortGenres += ","
      if cntGen < 3:
        shortGenres += gen

      cntGen += 1
    series_data.genres = genres
    print('Genres:       ' + genres)

    cast = ""
    shortCast = ""
    if 'cast' in series.data:
      i = 0
      for actor in series.data['cast']:
        cast += actor['name']
        cast += ", "
        if i < 5 :
          shortCast += actor['name']
        if i >= 0 and i < 4 :
          shortCast += ", "
        i = i + 1
              
      print('Cast:         ' + shortCast)
      series_data.cast_complete = cast
      series_data.cast_leads = shortCast
    else:
      print("-------------------------------------------")
      print("NO CAST!!!")
      print("-------------------------------------------")
        
    print ()
    plot = series.data.get('plot outline', None)
    series_data.plot = plot
    #print("Plot outline: " + str(plot))

  except:
    print("\nERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!\n")
    series_data.name = ""
  
  return series_data

