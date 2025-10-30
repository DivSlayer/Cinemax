import json
import os
import re

import webvtt
from django.http import HttpResponse
from django.shortcuts import render
import requests
from Cinemax.env import Env
from Movie.models import Movie, Audio as MovieAudio, Video, Subtitle as MovieSubtitle
from Movie.values import get_movie_root
from Serial.models import Serial, Episode, EpisodeSubtitle, Audio as EpisodeAudio
from Serial.values import get_serial_root

from django.utils.text import slugify

from Tool.mark_sub import MarkSub
from Utility.no_serializer import get_object

API_KEY = Env().API_KEY


# Create your views here.

def get_poster(obj, proxy=None):
    print(f"get posterproxy is: {proxy}")
    title = "+".join(obj.title.split(" ")[:-1]).lower()
    if type(obj) == Movie:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=en-US&query={title}&page=1&include_adult=true"
    else:
        url = f"https://api.themoviedb.org/3/search/tv?api_key={API_KEY}&language=en-US&query={title}&page=1&include_adult=true"
    print(url)
    response = requests.get(url, verify=False)
    response = json.loads(response.text)
    response = dict(response)
    for found in response["results"]:
        date = found["first_air_date"] if type(
            obj) == Serial else found["release_date"]
        date = str(date).split("-")[0]
        movie_year = obj.title.split(' ')[-1]
        if date == movie_year:
            original = str(found['original_title']) if type(obj) == Movie else str(found['original_name'])
            original = " ".join(slugify(original).split('-'))
            sluged_title = " ".join(slugify(' '.join(obj.title.split(' ')[:-1])).split('-'))
            # if original.lower() == sluged_title.lower():
            image_url = found["backdrop_path"].split('/')[1] if type(found["backdrop_path"]) == str else \
                found['poster_path'].split('/')[1]
            image_url = f"https://image.tmdb.org/t/p/original/{image_url}"
            print(f'url : {image_url}')
            if proxy is not None:
                req = requests.get(image_url,
                                   verify=False,
                                   proxies=proxy)
            else:
                req = requests.get(image_url, verify=False)
            folder = get_movie_root(obj, use_media=True) if type(obj) == Movie else get_serial_root(obj,
                                                                                                    use_media=True)
            os.makedirs(folder, exist_ok=True)
            new_path = folder + 'poster_img.jpg'
            with open(new_path, 'wb') as f:
                f.write(req.content)
            poster_img_name = new_path.replace('./media/', '')
            return poster_img_name
    return None


def get_safe_words(string):
    list_words = []
    for word in string.strip().split(" "):
        check = re.match(r"[0-9A-Za-z]", word)
        if check is not None:
            list_words.append(check.string.lower())
    input_string = ' '.join(list_words)
    input_string = input_string.encode("latin", "ignore")
    input_string = input_string.decode("utf-8", "ignore")
    input_string = input_string.replace("'", '')
    input_string = input_string.replace(":", "").lower()
    return input_string


def convert_vtt(path):
    try:
        webvtt.from_srt(path).save(path.replace('.srt', '') + '.vtt')
        return True
    except Exception as e:
        print(e)
        return False
