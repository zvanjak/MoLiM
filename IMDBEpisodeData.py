class IMDBEpisodeData(object):
  def __init__(self,episodeId):        # poziva se kod inicijalizacije
    self.episodeId = episodeId
    self.title = ""
    self.movieID = 0
    self.year = 0
    self.runtime = 0
    self.rating = 0.0
    self.votes = 0
    self.writers = ""
    self.genres = ""
    self.countries = ""
    self.languages = ""
    self.cast_leads = ""
    self.cast_complete = ""
    self.plot = ""
    
    self.episodes_list = []

    self.directors_list = []
    self.genres_list = []
    self.cast_list = []
    self.producers_list = []
    self.writers_list = []

