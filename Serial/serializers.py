from rest_framework import serializers
import json
from Category.serializers import CategorySerializer
from Cinemax.env import Env
from Country.serializers import CountrySerializer
from Movie.models import Movie
from Person.models import Person
from Rest.common_serializers import (
    SmallPersonSerializer,
    SmallSerialSerializer,
    SubtitleSerializer,
    SmallMovieSerializer,
    AudioSerializer,
)
from Serial.models import Serial, Season, Episode, EpisodeSubtitle, Audio
from Utility.views import get_size

SERVER = Env().get_server()


def all_serializer(obj):
    if type(obj) == Movie:
        return SmallMovieSerializer(obj).data
    if type(obj) == Serial:
        return SmallSerialSerializer(obj).data
    if type(obj) == Person:
        return SmallPersonSerializer(obj).data


class SerialSerializer(serializers.ModelSerializer):
    poster_img = serializers.SerializerMethodField("get_poster_img")
    item_img = serializers.SerializerMethodField("get_item_img")
    genre = serializers.SerializerMethodField("get_genre")
    country = serializers.SerializerMethodField("get_country")
    cast = serializers.SerializerMethodField("get_cast")
    writers = serializers.SerializerMethodField("get_writers")
    directors = serializers.SerializerMethodField("get_directors")
    seasons = serializers.SerializerMethodField("get_seasons")
    related = serializers.SerializerMethodField("get_related")
    suggestions = serializers.SerializerMethodField("get_suggestions")

    class Meta:
        model = Serial
        fields = [
            "pk",
            "imdb_id",
            "uuid",
            "slug",
            "fa_title",
            "title",
            "poster_img",
            "item_img",
            "rating",
            "year",
            "genre",
            "language",
            "country",
            "budget",
            "certificate",
            "resolution",
            "duration",
            "quotes",
            "en_story",
            "fa_story",
            "cast",
            "writers",
            "directors",
            "show_poster",
            "ultra",
            "published_at",
            "url",
            "seasons",
            "related",
            "suggestions",
        ]

    def get_poster_img(self, movie):
        return SERVER + movie.poster_img.url if movie.poster_img else None

    def get_item_img(self, movie):
        return SERVER + movie.item_img.url if movie.item_img else None

    def get_genre(self, movie):
        return CategorySerializer(movie.genre.all(), many=True).data

    def get_country(self, movie):
       return CountrySerializer(movie.country.all(), many=True).data
    
    def get_cast(self, movie):
        return SmallPersonSerializer(movie.cast.all(), many=True).data

    def get_writers(self, movie):
        return SmallPersonSerializer(movie.writers.all(), many=True).data

    def get_directors(self, movie):
        return SmallPersonSerializer(movie.directors.all(), many=True).data

    def get_seasons(self, serial):
        seasons = Season.objects.filter(serial=serial)
        return SeasonSerializer(seasons, many=True).data

    def get_related(self, movie):
        return []

    def get_suggestions(self, serial):
        suggestions = []
        all_genres = serial.genre.all()
        other_movies = [movie for movie in Movie.objects.all()]
        serials = [serial for serial in Serial.objects.all().exclude(uuid=serial.uuid)]
        other_movies.extend(serials)
        together = []
        for m_obj in other_movies:
            object_genre = m_obj.genre.all()
            status = True
            for genre in object_genre:
                if genre not in all_genres:
                    status = False
            if status:
                together.append(m_obj)
        return [all_serializer(obj) for obj in together[:5]]


class SeasonSerializer(serializers.ModelSerializer):
    collections = serializers.SerializerMethodField("get_collections")
    serial_slug = serializers.SerializerMethodField("get_serial_slug")

    class Meta:
        model = Season
        fields = ["pk", "number", "collections", "uuid", "serial_slug"]

    def get_collections(self, season):
        episodes = Episode.objects.filter(season=season)
        return EpisodeSerializer(episodes, many=True).data

    def get_serial_slug(self, season):
        return season.serial.slug


class EpisodeSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField("get_label")
    title = serializers.SerializerMethodField("get_title")
    size = serializers.SerializerMethodField("get_size")
    sizeb = serializers.SerializerMethodField("get_sizeb")

    class Meta:
        model = Episode
        fields = [
            "uuid",
            "label",
            "title",
            "size",
            "sizeb",
            "resolution",
            "number",
            "dubbed",
            "subbed",
        ]
    def get_label(self, episode):
        return f" قسمت {episode.number}"

    def get_title(self, episode):
        return f" قسمت {episode.number}"

    def get_size(self, episode):
        return episode.size if episode.size is not None else 0

    def get_sizeb(self, episode):
        return get_size(episode.video.path, bytes=True)

