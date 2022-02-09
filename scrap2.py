import sys
import requests
import lxml.html

def main(id):
    hxs = lxml.html.document_fromstring(requests.get("http://www.imdb.com/title/" + id).content)
    movie = {}
    try:
        movie['title'] = hxs.xpath('//*[@id="overview-top"]/h1/span[1]/text()')[0].strip()
    except IndexError:
        movie['title']
    try:
        movie['year'] = hxs.xpath('//*[@id="overview-top"]/h1/span[2]/a/text()')[0].strip()
    except IndexError:
        try:
            movie['year'] = hxs.xpath('//*[@id="overview-top"]/h1/span[3]/a/text()')[0].strip()
        except IndexError:
            movie['year'] = ""
    try:
        movie['certification'] = hxs.xpath('//*[@id="overview-top"]/div[2]/span[1]/@title')[0].strip()
    except IndexError:
        movie['certification'] = ""
    try:
        movie['running_time'] = hxs.xpath('//*[@id="overview-top"]/div[2]/time/text()')[0].strip()
    except IndexError:
        movie['running_time'] = ""
    try:
        movie['genre'] = hxs.xpath('//*[@id="overview-top"]/div[2]/a/span/text()')
    except IndexError:
        movie['genre'] = []
    try:
        movie['release_date'] = hxs.xpath('//*[@id="overview-top"]/div[2]/span[3]/a/text()')[0].strip()
    except IndexError:
        try:
            movie['release_date'] = hxs.xpath('//*[@id="overview-top"]/div[2]/span[4]/a/text()')[0].strip()
        except Exception:
            movie['release_date'] = ""
    try:
        movie['rating'] = hxs.xpath('//*[@id="overview-top"]/div[3]/div[3]/strong/span/text()')[0]
    except IndexError:
        movie['rating'] = ""
    try:
        movie['metascore'] = hxs.xpath('//*[@id="overview-top"]/div[3]/div[3]/a[2]/text()')[0].strip().split('/')[0]
    except IndexError:
        movie['metascore'] = 0
    try:
        movie['description'] = hxs.xpath('//*[@id="overview-top"]/p[2]/text()')[0].strip()
    except IndexError:
        movie['description'] = ""
    try:
        movie['director'] = hxs.xpath('//*[@id="overview-top"]/div[4]/a/span/text()')[0].strip()
    except IndexError:
        movie['director'] = ""
    try:
        movie['stars'] = hxs.xpath('//*[@id="overview-top"]/div[6]/a/span/text()')
    except IndexError:
        movie['stars'] = ""
    try:
        movie['poster'] = hxs.xpath('//*[@id="img_primary"]/div/a/img/@src')[0]
    except IndexError:
        movie['poster'] = ""
    try:
        movie['gallery'] = hxs.xpath('//*[@id="combined-photos"]/div/a/img/@src')
    except IndexError:
        movie['gallery'] = ""
    try:
        movie['storyline'] = hxs.xpath('//*[@id="titleStoryLine"]/div[1]/p/text()')[0].strip()
    except IndexError:
        movie['storyline'] = ""
    try:
        movie['votes'] = hxs.xpath('//*[@id="overview-top"]/div[3]/div[3]/a[1]/span/text()')[0].strip()
    except IndexError:
        movie['votes'] = ""
    return movie

print (main("tt1905041"))