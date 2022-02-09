import sys

import os
from os import listdir
from os.path import isfile, join

import requests
from bs4 import BeautifulSoup
import time
from colorama import init,Fore

def parse_movie(url):
    title = '-'
    summary = '-'
    cast = []
    record = {}

    try:
        url = url.rstrip('\n')
        print('Processing..' + url)
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None

        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        title_section = soup.select('.title_wrapper > h1')
        summary_section = soup.select('.plot_summary .summary_text')
        cast_list = soup.select('.cast_list')

        for i in range(len(soup.find_all('div', {'class': 'credit_summary_item'})[2].find_all('a')) - 1):
            print(soup.find_all('div', {'class': 'credit_summary_item'})[2].find_all('a')[i].text)
            cast.append(soup.find_all('div', {'class': 'credit_summary_item'})[2].find_all('a')[i].text)

        if summary_section:
            summary = summary_section[0].text.strip()

        if title_section:
            title = title_section[0].text.strip()
        #if cast_list:
        #    actors = cast_list[0].findAll('span', {'itemprop': 'name'})
        #    for actor in actors:
        #        cast.append(actor.text.strip())

            record = {'title': title, 'summary': summary, 'cast': cast}
    except Exception as ex:
        print(str(ex))
    finally:
        return record

def get_movie_data(movie):
    try:
        page = requests.get('http://www.imdb.com/find?ref_=nv_sr_fn&q=' + movie + '&s=tt');
        soup1 = BeautifulSoup(page.content, 'html.parser')
        movieid = soup1.select(".findList tr a")[0].get('href')
        movielink = "http://www.imdb.com" + movieid

        #rec = parse_movie(movielink)

        mlinkpage = requests.get(movielink)
        soup2 = BeautifulSoup(mlinkpage.content, 'html.parser')
        aba = soup2.select(".title_wrapper h1")
        titlenyear = soup2.select(".title_wrapper h1")[0].text
        movietitle = titlenyear[0:len(titlenyear) - 8]
        movieyear = titlenyear[len(titlenyear) - 6:len(titlenyear) - 2]
        movierating = soup2.select(".ratingValue span")[0].text
        metascore = soup2.select(".metacriticScore")
        metascore = metascore[0].text.strip() if metascore else None
        contentrating = soup2.find('meta',{'itemprop':'contentRating'})
        contentrating = contentrating['content'].strip() if contentrating else None
        movielength = soup2.select(".subtext time")[0].text.strip()
        genresndate = [i.text for i in soup2.select(".subtext a")]
        releasedate = genresndate[-1].strip()
        moviegenres = ""
        for i in soup2.find_all("div","txt-block"):
            if i.h4:
                if i.h4.text=="Budget:":
                    moviebudget = i.h4.next_element.next_element.strip()
                if i.h4.text=="Opening Weekend USA:":
                    movieopening = i.h4.next_element.next_element.strip()[:-1]
                if i.h4.text=="Gross USA:":
                    movieusagross = i.h4.next_element.next_element.strip()[:-1]
                if i.h4.text=="Cumulative Worldwide Gross:":
                    movieworldgross = i.h4.next_element.next_element.strip()[:-1]
                if i.h4.text=="Aspect Ratio:":
                    movieratio = i.h4.next_element.next_element.strip()
                if i.h4.text=="Taglines:":
                    movietaglines = i.h4.next_element.next_element.strip()
                if i.h4.text=="Also Known As:":
                    moviealsoknown = i.h4.next_element.next_element.strip()
                if i.h4.text=="Country:":
                    moviecountry = i.h4.next_sibling.next_element.text.strip()
        for x in range(len(genresndate) - 1):
            moviegenres = moviegenres + ',' + genresndate[x]
        moviegenres = moviegenres[1:]
        moviedesc = soup2.select(".summary_text")[0].text.strip()
        moviecast = [i.text for i in soup2.select(".credit_summary_item span a span")]
        movieactors = ""

        moviedirector = soup2.find_all('div', {'class': 'credit_summary_item'})[0].a.text

        for i in range(len(soup2.find_all('div', {'class': 'credit_summary_item'})[2].find_all('a')) - 1):
            actor_name = soup2.find_all('div', {'class': 'credit_summary_item'})[2].find_all('a')[i].text
            print(actor_name)
            movieactors = (movieactors + actor_name + ", ")

        if len(moviecast) > 5 :
            moviedirector = moviecast[0]
            movieactors = moviecast[3] + ',' + moviecast[4] + ',' + moviecast[5];

        print(Fore.LIGHTRED_EX + "Title: " + Fore.LIGHTGREEN_EX + movietitle)
        print(Fore.LIGHTRED_EX + "IMDB Rating: " + Fore.LIGHTYELLOW_EX + movierating + "/10")
        if metascore: print(Fore.LIGHTRED_EX + "Metascore: " + Fore.LIGHTYELLOW_EX + metascore + "/100")
        print(Fore.LIGHTRED_EX + "Length: " + Fore.LIGHTCYAN_EX + movielength)
        print(Fore.LIGHTRED_EX + "Year: " + Fore.LIGHTMAGENTA_EX + movieyear)
        print(Fore.LIGHTRED_EX + "Genre: " + Fore.LIGHTBLUE_EX + moviegenres)
        print(Fore.LIGHTRED_EX + "Description: " + Fore.LIGHTWHITE_EX + moviedesc)
        print(Fore.LIGHTRED_EX + "Release date: " + Fore.LIGHTCYAN_EX + releasedate)
        if contentrating: print(Fore.LIGHTRED_EX + "Rating: " + Fore.LIGHTCYAN_EX + contentrating)
        print(Fore.LIGHTRED_EX + "Director: " + Fore.LIGHTBLACK_EX + moviedirector)
        print(Fore.LIGHTRED_EX + "Lead Cast: " + Fore.LIGHTBLACK_EX + movieactors)
        print(Fore.LIGHTRED_EX + "Country: " + Fore.LIGHTBLUE_EX + moviecountry)
        print(Fore.LIGHTRED_EX + "Also Known As: " + Fore.LIGHTBLUE_EX + moviealsoknown)
        print(Fore.LIGHTRED_EX + "Budget: " + Fore.LIGHTBLUE_EX + moviebudget)
        print(Fore.LIGHTRED_EX + "Opening Weekend USA: " + Fore.LIGHTBLUE_EX + movieopening)
        print(Fore.LIGHTRED_EX + "Gross USA: " + Fore.LIGHTBLUE_EX + movieusagross)
        print(Fore.LIGHTRED_EX + "Cumulative Worldwide Gross: " + Fore.LIGHTBLUE_EX + movieworldgross)
        print(Fore.LIGHTRED_EX + "Ratio: " + Fore.LIGHTBLUE_EX + movieratio)
        print(Fore.LIGHTRED_EX + "Taglines: " + Fore.LIGHTBLUE_EX + movietaglines)
    except:
        print(Fore.LIGHTRED_EX+"Something's wrong,Try Again Later")

#main
init(convert=True)
headers = {'headers': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}

print(Fore.LIGHTBLACK_EX+"Loading...")
time.sleep(0.5)
print(Fore.LIGHTBLACK_EX+"Please wait...\n")

get_movie_data("Dunes")

