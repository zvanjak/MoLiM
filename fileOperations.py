
from datetime import date

import os

def getFolderSize(start_path : str):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def getNameYearFromNameWithIMDB(movieFolderName : str) :
  ind1 = movieFolderName.find("(")
  ind2 = movieFolderName.find(")")

  imdb_name_raw = movieFolderName[0:ind1-1]
  if imdb_name_raw.startswith("zzz"):
    imdb_name1 = movieFolderName[4:ind1-1]
  else:
    imdb_name1 = imdb_name_raw

  imdb_name = imdb_name1.strip("_") 
  year_str  = movieFolderName[ind1+1:ind2]

  return (imdb_name, year_str)
