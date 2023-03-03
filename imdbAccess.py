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
import IMDBSeriesData
import IMDBSeriesSeasonData
import IMDBEpisodeData


# create an instance of the Cinemagoer class
ia = Cinemagoer()


# fetchMovieData(searchMovieName, releaseYear)
def fetchMovieData(searchMovieName, releaseYear) -> IMDBMovieData:
  movie_data = IMDBMovieData.IMDBMovieData(searchMovieName)

  searchMovieName = searchMovieName.rstrip()

  # TODO kad internet zakae
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
  series_data = IMDBMovieData.IMDBMovieData(searchMovieName)

  searchMovieName = searchMovieName.rstrip()

  # TODO kad internet zakae
  try:
    foundMoviesList = ia.search_movie(searchMovieName)
  except:
    print("\n--------   EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET --------\n")
    time.sleep(30)
    series_data.name = ""
    return series_data

  if len(foundMoviesList) == 0 :
    series_data.name = ""
    print ("\n   ----   SEARCH RETURNED NOTHING!!!   ----\n")
    time.sleep(20)
    return series_data

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

  series_data = fetchSeriesDataByMovieID(searchMovieName, movieID)

  time.sleep(5+random.randrange(0,5))

  return series_data


def fetchSeriesDataByMovieID(name : str, movieID : str) -> IMDBSeriesData.IMDBSeriesData:
  series_data = IMDBSeriesData.IMDBSeriesData(name)

  try:
     imdb_series_data = ia.get_movie(movieID)

     ia.update(imdb_series_data, 'episodes')

  except:
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    print("EEEE, JEEEBIII GAAAA!!!! OSSSOO INTERNET")
    time.sleep(30)
    series_data.name = ""
    return series_data

  series_data.movieID = movieID

  try:
    series_data.imdb_name = imdb_series_data.data.get('title')

    rating = imdb_series_data.data.get('rating', None)
    series_data.rating = rating
    print("IMDB rating:  {0}".format(rating))

    votes = imdb_series_data.data.get('votes', 0)
    series_data.votes = votes
    print("Num. votes:   {0}".format(votes))

    year = imdb_series_data.data.get('year', None)
    series_data.year = year
    print("Year:         {0}".format(year))

    if 'runtimes' in imdb_series_data.data:
      runtime = int(imdb_series_data.data['runtimes'][0])
      series_data.runtime = runtime
      print("Runtime:     ", runtime, " min")
    else:
      print("-------------------------------------------")
      print("NO RUNTIME!!!!")
      print("-------------------------------------------")
      series_data.runtime = 0

    if 'countries' in imdb_series_data.data:
      series_data.countries = str(imdb_series_data.data['countries'])

    if 'languages' in imdb_series_data.data:
      series_data.languages = str(imdb_series_data.data['languages'])
      
    writers = ""
    cntWrit = 0
    if 'writer' in imdb_series_data.data:
      movieWriters = imdb_series_data.data.get('writer')
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
    for gen in imdb_series_data.data['genres']:
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
    if 'cast' in imdb_series_data.data:
      i = 0
      for actor in imdb_series_data.data['cast']:
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
    plot = imdb_series_data.data.get('plot outline', None)
    series_data.plot = plot
    print("Plot outline: " + str(plot))

    season_keys = sorted(imdb_series_data['episodes'].keys())

    num_seasons = len(imdb_series_data['episodes'].keys())
    print("Seasons num = {0}".format(num_seasons))
    series_data.num_seasons = num_seasons

    for season_id in season_keys:
      new_season = IMDBSeriesSeasonData.IMDBSeriesSeasonData(season_id)
      
      series_data.seasons_list.append(new_season)
      season_data = imdb_series_data['episodes'][season_id]
      episode_num = len(season_data)
      new_season.num_episodes = episode_num

      print("Season {0}".format(season_id))    
      print("Episode num = {0}".format(episode_num))

      season_episodes_keys = imdb_series_data['episodes'][season_id].keys()
      for season_episode_key_id in season_episodes_keys:
        episode = imdb_series_data['episodes'][season_id][season_episode_key_id]

        new_episode = IMDBEpisodeData.IMDBEpisodeData(season_episode_key_id)
        new_season.episodes_list.append(new_episode)

        new_episode.title = episode['title']

        rating = episode.data.get('rating', None)
        new_episode.rating = rating

        votes = episode.data.get('votes', None)
        new_episode.votes = votes

        original_air_date = episode.data.get('originalair date', None)
        new_episode.original_air_date = original_air_date

        year = episode.data.get('year', None)
        new_episode.year = year

        plot = episode.data.get('plot', None)
        new_episode.plot = plot

  except:
    print("\nERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!\n")
    series_data.name = ""
  
  return series_data

