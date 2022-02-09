# import both Requests and Beautifulsoup

import requests

from bs4 import BeautifulSoup


class IMDBScraper:


   def __init__(self, url):

       self.url = url

       self.download_page()



   def download_page(self):

       # method for downloading the hotel page

       self.page = requests.get(self.url).text
   
   def scrape_data(self):

       #method for scraping out movie title and description

       soup = BeautifulSoup(self.page, "html.parser")

       movie_title = soup.find("h1", {"data-testid": "hero-title-block__title"}).text

       movie_description = soup.find("span", {"data-testid": "plot-xl"}).text

       return {"title": movie_title,

               "description": movie_description,

               }



urls = ["https://www.imdb.com/title/tt2382320/?ref_=hm_fanfav_tt_i_3_pd_fp1",]

for url in urls:

   x = IMDBScraper(url)

   print(x.scrape_data())