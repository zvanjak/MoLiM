
# Underscore functionality

# UNDERSCORE RATING
def setFolderNameUnderscoreRating(folderName, movieFolderName, imdbRating):
  m1 = movieFolderName.strip("zzz")
  realMovieName = m1.strip("_")

  # strip sve underscore na poečtku
  if imdbRating >= 9.0:
    origDir = folderName + "\\" + movieFolderName
    destDir = folderName + "\\" + "___" + realMovieName
    print("RENAMING - ", origDir, destDir)
    os.rename(origDir, destDir)
  elif imdbRating >= 8.0:
    origDir = folderName + "\\" + movieFolderName
    destDir = folderName + "\\" + "__" + realMovieName
    print("RENAMING - ", origDir, " -> ", destDir)
    os.rename(origDir, destDir)
  elif imdbRating >= 7.0:
    origDir = folderName + "\\" + movieFolderName
    destDir = folderName + "\\" + "_" + realMovieName
    print("RENAMING - ", origDir, destDir)
    os.rename(origDir, destDir)
  elif imdbRating >= 6.0:
    origDir = folderName + "\\" + movieFolderName
    destDir = folderName + "\\" + realMovieName
    print("RENAMING - ", origDir, destDir)
    os.rename(origDir, destDir)
  elif imdbRating < 6.0:
    origDir = folderName + "\\" + movieFolderName
    destDir = folderName + "\\" + "zzz_" + realMovieName
    print("RENAMING - ", origDir, destDir)
    os.rename(origDir, destDir)

def folderReapplyUnderscoreRating(folderName):
  print("------", folderName, "------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]
  
  listNotDone = []
  for movieFileName in movieSubFolders:
    if movieFileName.find("IMDB") != -1:
      ind = movieFileName.find("IMDB")
      imdb_rat_str = movieFileName[ind+5:ind+8]
      imdb_rat = float(imdb_rat_str)
      
      ind = movieFileName.find("(")
      imdb_name = movieFileName[0:ind-1]

      underscore_rat = 0
      if imdb_name.startswith("___"):
        if imdb_rat < 9.0:
          print("ERRROR - ", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
      elif imdb_name.startswith("__"):
        if imdb_rat < 8.0:
          print("ERRROR - ", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
        elif imdb_rat >= 9.0:
          print("ERROR - SHOULD BE HIGHER", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
      elif imdb_name.startswith("_"):
        if imdb_rat < 7.0:
          print("ERRROR - ", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
        elif imdb_rat >= 8.0:
          print("ERROR - SHOULD BE HIGHER", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
      elif imdb_name.startswith("_") == False and imdb_rat >= 7.0:
        print("ERROR - SHOULD BE HIGHER", movieFileName)
        setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)
      elif imdb_name.startswith("zzz_"):
        if imdb_rat >= 6.0:
          print("ERRROR - ", movieFileName)
          setFolderNameUnderscoreRating(folderName, movieFileName, imdb_rat)

# UNDERSCORE STATISTICS
def folderUnderscoreStatistics(folderName):
  print("------", folderName, "------")

  movieSubFolders = [ f.name for f in os.scandir(folderName) if f.is_dir() ]
  
  listNotDone = []
  for movieFileName in movieSubFolders:
    if movieFileName.find("IMDB") != -1:
      ind = movieFileName.find("IMDB")
      imdb_rat_str = movieFileName[ind+5:ind+8]
      imdb_rat = float(imdb_rat_str)
      ind = movieFileName.find("(")
      imdb_name = movieFileName[0:ind-1]

      underscore_rat = 0
      if imdb_name.startswith("___"):
        if imdb_rat < 9.0:
          print("ERRROR - ", movieFileName)
      elif imdb_name.startswith("__"):
        if imdb_rat < 8.0:
          print("ERRROR - ", movieFileName)
        elif imdb_rat >= 9.0:
          print("ERROR - SHOULD BE HIGHER", movieFileName)
      elif imdb_name.startswith("_"):
        if imdb_rat < 7.0:
          print("ERRROR - ", movieFileName)
        elif imdb_rat >= 8.0:
          print("ERROR - SHOULD BE HIGHER", movieFileName)
      elif imdb_name.startswith("_") == False and imdb_rat >= 7.0:
        print("ERROR - SHOULD BE HIGHER", movieFileName)
      elif imdb_name.startswith("zzz_"):
        if imdb_rat >= 6.0:
          print("ERRROR - ", movieFileName)
        
def rootFolderUnderscoreStatistics(rootFolderName):
  print("------", rootFolderName, "------")
  
  rootSubFolders = [ f.path for f in os.scandir(rootFolderName) if f.is_dir() ]

  for folderName in rootSubFolders:
    folderUnderscoreStatistics(folderName)
 