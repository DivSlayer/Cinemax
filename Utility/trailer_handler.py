import json
import os.path

import requests
from pytube import YouTube

from Movie.models import Movie, Trailer as MovieTrailer
from Movie.values import get_movie_root
from Serial.models import Serial, Trailer as SerialTrailer
from Serial.values import get_serial_root
from Tool.views import get_safe_words
from Utility.no_serializer import get_object
from Utility.views import get_duration, get_resolution, get_size


class TrailerHandler:
    def __init__(self, imdb_id, proxy=None):
        self.imdb_id = imdb_id
        self.api_key = "a776ea545eb6eb3d6f014ed9946b8cc8"
        self.movie_id = None
        self.obj = None
        self.proxy = proxy
        self.keys = []
        self.done = []

    def start(self):
        self.obj = get_object(self.imdb_id, use_imdb=True)
        self.get_video_id()
        if self.movie_id is not None:
            self.get_video_keys()
            self.get_key_video()
        return self.done

    def get_video_id(self):
        title = "+".join(self.obj.title.split(" ")[:-1]).lower()
        if type(self.obj) == Movie:
            url = f"https://api.themoviedb.org/3/search/movie?api_key={self.api_key}&language=en-US&query={title}&page=1&include_adult=true"
        else:
            url = f"https://api.themoviedb.org/3/search/tv?api_key={self.api_key}&language=en-US&query={title}&page=1&include_adult=true"
        print(f"url: {url}")
        response = requests.get(url, verify=False)
        response = json.loads(response.text)
        response = dict(response)
        for found in response["results"]:
            date = found["first_air_date"] if type(
                self.obj) == Serial else found["release_date"]
            date = str(date).split("-")[0]
            movie_year = self.obj.title.split(' ')[-1]
            if date == movie_year:
                if str(found['original_title']).lower() == ' '.join(self.obj.title.split(' ')[:-1]).lower():
                    self.movie_id = found['id']

    def get_video_keys(self):
        if type(self.obj) == Movie:
            url = f"https://api.themoviedb.org/3/movie/{self.movie_id}/videos?api_key={self.api_key}"
        else:
            url = f"https://api.themoviedb.org/3/tv/{self.movie_id}/videos?api_key={self.api_key}"
        response = requests.get(url, verify=False)
        response = json.loads(response.text)
        response = dict(response)
        results = response['results'] if 'results' in response.keys() else []
        for result in results:
            self.keys.append(result['key'])

    def video_filter(self, title: str, length):
        condition = True
        if length > 130:
            condition = False
        if title.lower().find('trailer') == 0:
            condition = False
        return condition

    def get_key_video(self):
        for key in self.keys:
            print(key)
            url = f'https://youtube.com/watch?v={key}'
            py = YouTube(url)
            title = py.title
            title = get_safe_words(title)
            filtered = self.video_filter(title, py.length)

            if filtered:
                stream = py.streams.filter(progressive=True, file_extension='mp4').order_by(
                    'resolution').desc().first()
                print(py.length)
                self.download_video(stream, f"{title}.mp4")

    def download_video(self, stream, title):
        folder = get_movie_root(self.obj, filepath='trailers/', use_media=True) if type(
            self.obj) == Movie else get_serial_root(
            self.obj, filepath='trailers/', use_media=True)
        os.makedirs(folder, exist_ok=True)
        stream.download(output_path=folder, filename=title)
        file_name = folder.replace('media/', '') + f"{title}"
        self.make_trailer_ins(file_name=file_name, title=title, file_path=folder + f"{title}")

    def make_trailer_ins(self, file_name, title: str, file_path):
        trailer_instance = MovieTrailer.objects.create(movie=self.obj) if type(
            self.obj) == Movie else SerialTrailer.objects.create(serial=self.obj)
        trailer_instance.label = title
        trailer_instance.file.name = file_name
        trailer_instance.duration = get_duration(file_path)
        trailer_instance.resolution = get_resolution(file_path)
        trailer_instance.size = get_size(file_path)
        trailer_instance.save()
        self.done.append(trailer_instance)
