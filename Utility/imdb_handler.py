import asyncio
import datetime
import json
import os

import requests
from bs4 import BeautifulSoup
from imdb import Cinemagoer
from Cinemax.env import Env
from Country.models import Country
from Movie.models import Movie
from Serial.models import Serial
from Serial.values import get_serial_root
from Movie.values import get_movie_root
from Tag.models import Tag
from Tool.get_colors import GetColors
from Tool.get_qrCode import GetQRCode
from Tool.views import get_poster
from Utility.actor_handler import ActorHandler
from Utility.bsoup_parser import BsoupParser
from Utility.category_handler import CategoryHandler
from PIL import Image

from Utility.translator import translate_text

API_KEY = Env().API_KEY


class IMDBHandler:
    def __init__(self, movie, proxy=None, get_image=False, get_poster=True):
        self.movie = movie
        self.parser = None
        self.title = None
        self.poster_img = None
        self.item_img = None
        self.compress_img = None
        self.rating = None
        self.year = None
        self.genre = []
        self.language = None
        self.country = None
        self.budget = None
        self.certificate = None
        self.quotes = None
        self.en_story = None
        self.fa_story = None
        self.cast = []
        self.writers = []
        self.directors = []
        self.qrCode = None
        self.freq_color = None
        self.second_color = None
        self.third_color = None
        self.proxy = proxy
        self.get_image = get_image
        self.get_poster_c = get_poster
        self.xml_path = os.path.join(os.getcwd(), f"media/xmls/{movie.imdb_id}-xml.xml")

    def start(self):
        try:
            print("I'm Working")
            self.connect_imdb()
            self.next_step()
            if os.path.isfile(self.xml_path):
                os.remove(self.xml_path)
            return self.movie, self.poster_img is not None
        except Exception as e:
            print(f"\n[IMDB HANDLER ERROR] {e}\n")
            # raise e
            if os.path.isfile(self.xml_path):
                os.remove(self.xml_path)
            self.start()

    def next_step(self):
        self.get_infos()
        if self.get_poster_c:
            if not self.movie.poster_img or self.movie.poster_img == None:
                self.get_poster_img()
        if self.get_image:
            if not self.movie.item_img or self.movie.item_img == None:
                self.get_item_img()
                self.make_compress_img()
                self.get_colors()
        self.get_cast()
        print("get writers")
        self.get_writers()
        print("get directors")
        self.get_directors()
        print("get qrcode")
        self.make_qrcode()
        self.get_genre()
        self.get_tags()

    def connect_imdb(self):
        print("im working")
        ia = Cinemagoer()
        ia_movie = ia.get_movie(self.movie.imdb_id)
        with open(self.xml_path, "w", encoding="utf-8") as f:
            f.write(ia_movie.asXML())
        with open(self.xml_path, "r", encoding="utf-8") as f:
            data = f.read()
        bs_data = BeautifulSoup(data, "xml")
        parser = BsoupParser(bs_data)
        self.parser = parser

    def get_infos(self):
        self.title = self.parser.find_item("localized-title").text()
        self.item_img = self.parser.find_item("full-size-cover-url").text()
        self.en_story = self.parser.find_item("plot").text()
        translated = asyncio.run(translate_text(str(self.en_story)))
        self.fa_story = translated if self.en_story else None

        self.year = self.parser.find_item("year").text()
        self.budget = self.parser.find_item("box-office").find_item("budget").text()
        self.language = ", ".join(
            self.parser.find_item("languages").find_all("item").for_list()
        )
        self.country = ", ".join(
            self.parser.find_item("countries").find_all("item").for_list()
        )
        self.certificate = "".join(
            [
                element.split(":")[1].split("(")[0].strip()
                if element.split(":")[0] == "United States"
                else ""
                for element in self.parser.find_item("certificates")
            .find_all("item")
            .for_list()
            ]
        )
        self.title = f"{self.title} {self.year}"
        self.rating = self.parser.find_item("rating").text()
        self.movie.title = self.title
        translated_title = asyncio.run(translate_text(str(self.title)))
        self.movie.fa_title = translated_title
        self.movie.year = self.year
        self.movie.rating = self.rating
        self.movie.language = self.language
        self.movie.country.set(self.handle_country())
        self.movie.budget = self.budget
        self.movie.certificate = self.certificate
        self.movie.en_story = self.en_story
        self.movie.fa_story = self.fa_story
        print("saving movie")
        self.movie.save()
        print("get_release")
        self.get_release()

    def handle_country(self):
        country_list = [c.strip().lower() for c in self.country.split(",")]
        countries_ins = []
        for c in country_list:
            found = Country.objects.filter(name=c)
            if len(found) > 0:
                countries_ins.append(found.first())
        return countries_ins

    def get_item_img(self, file_name="item_img.jpg"):
        if self.item_img is not None:
            detail_req = requests.get(self.item_img)
            path = (
                get_movie_root(movie=self.movie, use_media=True)
                if type(self.movie) == Movie
                else get_serial_root(self.movie, use_media=True)
            )
            os.makedirs(path, exist_ok=True)
            detail_path = path + file_name
            open(detail_path, "wb").write(detail_req.content)
            item_name = (
                get_movie_root(self.movie, "item_img.jpg")
                if type(self.movie) == Movie
                else get_serial_root(self.movie, "item_img.jpg")
            )
            self.item_img = item_name
            self.movie.item_img.name = self.item_img

    def get_release(self):
        title = "+".join(self.movie.title.split(" ")[:-1]).lower()
        if type(self.movie) == Movie:
            url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=en-US&query={title}&page=1&include_adult=true"
        else:
            url = f"https://api.themoviedb.org/3/search/tv?api_key={API_KEY}&language=en-US&query={title}&page=1&include_adult=true"
        print(f"release url : {url}")
        response = requests.get(url, verify=False)
        response = json.loads(response.text)
        response = dict(response)
        for found in response["results"]:
            date = date_dict = (
                found["first_air_date"]
                if type(self.movie) == Serial
                else found["release_date"]
            )
            date = str(date).split("-")[0]
            movie_year = self.movie.title.split(" ")[-1]
            original_name = (
                found["original_name"]
                if type(self.movie) == Serial
                else found["original_title"]
            )
            # if date == movie_year and original_name.lower() == " ".join(self.movie.title.split(' ')[:-1]).lower():
            if date == movie_year:
                date_f = datetime.date.fromisoformat(date_dict)
                self.movie.release_date = date_f
                self.movie.save()

    def make_compress_img(self):
        image = Image.open(f"media/{self.item_img}")
        img_path = (
            f"{get_movie_root(self.movie, use_media=True)}compress_img.jpg"
            if type(self.movie) == Movie
            else f"{get_serial_root(self.movie, use_media=True)}compress_img.jpg"
        )
        image.save(img_path, "JPEG", optimize=True, quality=10)
        self.compress_img = (
            f"{get_movie_root(self.movie, use_media=False)}compress_img.jpg"
            if type(self.movie) == Movie
            else f"{get_serial_root(self.movie, use_media=False)}compress_img.jpg"
        )
        self.movie.compress_img.name = self.compress_img

    def get_poster_img(self):
        print(f"proxy: {self.proxy}")
        poster = get_poster(self.movie, self.proxy)
        if poster is not None:
            self.poster_img = poster.replace("media/", "")
            self.movie.poster_img.name = self.poster_img
            self.movie.save()

    def make_qrcode(self):
        qr_code = GetQRCode(self.movie.imdb_id)
        self.movie.qrCode = qr_code.start()
        self.movie.save()

    def get_colors(self):
        print(f"item_img: {self.item_img}")
        colors_ins = GetColors(f"media/{self.item_img}")
        self.freq_color, self.second_color, self.third_color = colors_ins.get_colors()

        self.movie.freq_color = self.freq_color
        self.movie.second_color = self.second_color
        self.movie.third_color = self.third_color
        self.movie.save()

    def get_cast(self):
        cast = self.parser.find_item("cast").find_all("person").for_list(raw=True)[:20]
        for actor in cast:
            actor_parser = BsoupParser(actor)
            actor_id = actor_parser.text(attr="id")
            actor_name = actor_parser.find_item("name").text()
            if actor_id:
                actor_instance = ActorHandler(actor_id, actor_name)
                actor_model_obj = actor_instance.start()
                if actor_model_obj is not None:
                    if actor_model_obj.name is not None:
                        if actor_model_obj.img:
                            self.cast.append(actor_model_obj)

        self.movie.cast.set(self.cast)
        self.movie.save()

    def get_directors(self):
        directors = (
            self.parser.find_item("director").find_all("person").for_list(raw=True)[:20]
        )
        for director in directors:
            director_parser = BsoupParser(director)
            director_id = director_parser.text(attr="id")
            director_name = director_parser.find_item("name").text()
            if director_id:
                director_instance = ActorHandler(director_id, director_name).start()
                if director_instance is not None:
                    if director_instance.name is not None:
                        if director_instance.img:
                            self.directors.append(director_instance)

        self.movie.directors.set(self.directors)
        self.movie.save()

    def get_writers(self):
        writers = (
            self.parser.find_item("writer").find_all("person").for_list(raw=True)[:20]
        )
        for writer in writers:
            writer_parser = BsoupParser(writer)
            writer_id = writer_parser.text(attr="id")
            writer_name = writer_parser.find_item("name").text()
            if writer_id:
                # writer_instance = self.handle_person(writer_id, writer_name, save_writer_db, writer, 'media/writers')
                writer_instance = ActorHandler(writer_id, writer_name).start()
                if writer_instance is not None:
                    if writer_instance.name is not None:
                        if writer_instance.img:
                            self.writers.append(writer_instance)

        self.movie.writers.set(self.writers)
        self.movie.save()

    def get_genre(self):
        for genre in self.parser.find_item("genres").find_all("item").for_list()[:3]:
            new_genre = CategoryHandler(str(genre).lower()).start()
            self.genre.append(new_genre)

        self.movie.genre.set(self.genre)
        self.movie.save()

    def get_tags(self):
        tags = []
        for genre in self.genre:
            if genre.en_title == "animation":
                tags.append(Tag.objects.get(url="anime"))
        if len(tags) == 0:
            main_tag = (
                Tag.objects.get(url="movie")
                if type(self.movie) == Movie
                else Tag.objects.get(url="serial")
            )
            tags.append(main_tag)
        self.movie.tags.set(tags)
        self.movie.save()
