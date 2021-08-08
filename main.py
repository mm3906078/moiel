#!/usr/bin/python
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from pymongo import *
import os
import requests
import sys
import zipfile
import glob
import shutil
import imdb
import json
client = "mongoclient"
moviesDB = imdb.IMDb()
#make
def data_Save(input):
    clinet = MongoClient(client)
    db = clinet.get_database("movies_db")
    rec = db.movies_dt
    rec.insert_many(input)

def data_exist(input):
    clinet = MongoClient(client)
    db = clinet.get_database("movies_db")
    rec = db.movies_dt
    return rec.find_one(input)

def find_link(url):
    ua = UserAgent()
    header = {"User-Agent": ua.random}
    page = requests.get(url, headers=header)
    soup = BeautifulSoup(page.content, 'html.parser')
    # find use class(dosent work!!)
    # title = soup.find_all(lambda tag: tag.name ==
    #                       'div' and tag.get('class') == ['dlblock'])
    title = ""
    for a in soup.find_all('a', href=True):
        if(a['href'].find("uploads") != -1):
            title = a['href']
    return title

def zip(path_to_file, title):
    directory = sys.path[0]
    directory = directory.replace("\\", '/')
    final_directory = f"{directory}/srt"

    if not os.path.exists(final_directory):
        os.makedirs(final_directory)

    if (os.path.isfile(f"{final_directory}/{title}") == False):
        with zipfile.ZipFile(path_to_file, 'r') as zip_ref:
            zip_ref.extractall(f"{final_directory}")

def strtojson(path_to_srt, movie_title):
    f = open(path_to_srt, "r")
    text = str(f.read())
    lines = text.split('\n')
    bufer = {
        "title": "",
        "id": "",
        "start_time": "",
        "end_time": "",
        "countent": ""
    }
    output = []
    counter = 0
    for l in lines:
        for char in (l):
            if(ord(char) > 122 or ord(char) == 64):
                l = l.replace(char, "")
        if(counter == 0 and l != ""):
            bufer["title"] = movie_title
            bufer["id"] = l
            counter += 1
            continue
        if(counter == 1 and l != ""):
            temp = l.split('-->')
            bufer["start_time"] = temp[0][:8]
            bufer["end_time"] = temp[1][:9]
            counter += 1
            continue
        if(counter == 2 and l != ""):
            bufer["countent"] = l
            counter += 1
            continue
        if(l == "" or counter == 3):
            if(bufer["title"] == "" and bufer["id"] == "" and bufer["start_time"] == "" and bufer["end_time"] == "" and bufer["countent"] == ""):
                continue
            output.append(bufer.copy())
            counter = 0
            bufer["title"] = ""
            bufer["id"] = ""
            bufer["start_time"] = ""
            bufer["end_time"] = ""
            bufer["countent"] = ""
            continue

    return output

def make():
    input = open("250_imdb.txt", "r")
    for each in input:
        movie_title = each.replace(" ", "-")
        movie_title = movie_title.replace(":", "")
        movie_title = movie_title.replace('\n', '')
        movie_url = ""

        movies = moviesDB.search_movie(movie_title)
        id = movies[0].getID()
        movie = moviesDB.get_movie(id)
        year = movie['year']

        # movie_url = f"https://subf2m.co/subtitles/{movie_title}/english/"
        movie_url = f"https://subkade.ir/%D8%AF%D8%A7%D9%86%D9%84%D9%88%D8%AF-%D8%B2%DB%8C%D8%B1%D9%86%D9%88%DB%8C%D8%B3-%D9%81%DB%8C%D9%84%D9%85-{movie_title}-{year}"

        path = sys.path[0]
        path = path.replace("\\", '/')
        new_path = f"{path}/zips"

        final_zip_path = f'{path}/zips/{movie_title}.zip'
        try:
            if not os.path.exists(new_path):
                os.makedirs(new_path)

            if (os.path.isfile(f"zips/{movie_title}.zip") == False):
                link = find_link(movie_url)
                r = requests.get(link)
                with open(final_zip_path, 'wb') as f:
                    f.write(r.content)

            zip(final_zip_path, movie_title)

            each = each.replace('\n', '')
            each = each.replace(":", "")
            site_title = f"{each} {year}"
            final_srt_path = f"srt/{site_title}/English"
            if os.path.exists(f"{path}/srt/{site_title}"):
                shutil.rmtree(f"{path}/srt/{site_title}/Persian")
                os.remove(f"{path}/srt/{site_title}/WWW.SUBKADE.IR.url")
                os.remove(
                    f"{path}/srt/{site_title}/English/WWW.SUBKADE.IR.url")

            size = 0
            os.chdir(final_srt_path)
            for file in glob.glob("*.srt"):
                if(os.path.getsize(f"{path}/{final_srt_path}/{file}") > size):
                    size = os.path.getsize(f"{path}/{final_srt_path}/{file}")
                    path_to_srt = f"{path}/{final_srt_path}/{file}"
                else:
                    os.remove(file)

            os.chdir(path)
            js = strtojson(path_to_srt, f"{movie_title}-{year}")
            if (os.path.isfile(f"js/{movie_title}.json") == False):
                file = open(f"js/{movie_title}.json", "w")
                file.write(json.dumps(js))
            if(data_exist({"title": f"{movie_title}-{year}"}) == None):
                data_Save(js)
        except:
            print(f"FAILD ON {movie_title}")
            pass
#search
def find_array(input):
    client = MongoClient(client)
    result = client['movies_db']['movies_dt'].aggregate([
        {
            '$search': {
                'text': {
                    'query': input,
                    'path': 'countent'
                }
            }
        }
    ])
    return result  

def find_how_many_time(input):
    bufer = {}
    for item in input:
        try:
            bufer[item['title']] += 1
        except:
            bufer[item['title']] = 1
            pass
    return bufer

def search(input):
    arr = find_array(input)
    res = find_how_many_time(arr)
    print(res)


# make()
# search("How")