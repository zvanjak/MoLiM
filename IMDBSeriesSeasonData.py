class IMDBSeriesSeasonData(object):
  def __init__(self,seasonID):        # poziva se kod inicijalizacije
    self.seasonID = seasonID
    self.movieID = 0
    self.year = 0
    self.runtime = 0
    self.rating = 0.0
    self.votes = 0
    self.writers = ""
    self.genres = ""
    self.countries = ""
    self.languages = ""
    self.cover_url = ""
    self.cast_leads = ""
    self.cast_complete = ""
    self.plot = ""
    
    self.directors_list = []
    self.genres_list = []
    self.cast_list = []
    self.producers_list = []
    self.writers_list = []

