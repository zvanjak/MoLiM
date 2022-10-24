
class IMDBMovieData(object):
  def __init__(self,name):        # poziva se kod inicijalizacije
    self.name = name
    self.imdb_name = ""
    self.movieID = 0
    self.year = 0
    self.runtime = 0
    self.rating = 0.0
    self.votes = 0
    self.directors = ""
    self.producers = ""
    self.writers = ""
    self.genres = ""
    self.countries = ""
    self.languages = ""
    self.cover_url = ""
    self.cast_leads = ""
    self.cast_complete = ""
    self.plot = ""
    
    self.box_office = ""
    self.top250rank = 0
    self.releaseDate = ""
    
    self.directors_list = []
    self.genres_list = []
    self.cast_list = []
    self.producers_list = []
    self.writers_list = []

  def isDirectedBy(self, director : str) -> bool:
    if self.directors.find(director) != -1:
      return True
    else:
      return False

  def hasGenre(self, genre: str) -> bool:
    return genre in self.genres

  def hasActor(self, actor: str) -> bool:
    return actor in self.cast_complete[0:300]
  

def printMoviesList(listMovies):
  for movie in listMovies:
    short_cast = movie.cast_complete[0:75]
    short_dir = movie.directors[0:20]
    print("Rating - {0} - {1:55} - {2:75}  -  {3:20}  - {4}".format( movie.rating, movie.name + " (" + str(movie.year) + ") ", short_cast, short_dir, movie.genres ) )
