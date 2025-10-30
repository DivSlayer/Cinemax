from django.conf import settings
from rest_framework import serializers

from Category.serializers import CategorySerializer
from Country.serializers import CountrySerializer
from Movie.models import Movie, Subtitle, Audio, Video
from Person.models import Person
from Rest.common_serializers import (
    SmallPersonSerializer,
    get_collection,
    SubtitleSerializer,
    AudioSerializer,
    SmallSerialSerializer,
    SmallMovieSerializer,
)
from Serial.models import Serial

SERVER = settings.SITE_URL.rstrip('/')


def all_serializer(obj):
    if type(obj) == Movie:
        return SmallMovieSerializer(obj).data
    if type(obj) == Serial:
        return SmallSerialSerializer(obj).data
    if type(obj) == Person:
        return SmallPersonSerializer(obj).data


class MovieSerializer(serializers.ModelSerializer):
    poster_img = serializers.SerializerMethodField("get_poster_img")
    item_img = serializers.SerializerMethodField("get_item_img")
    genre = serializers.SerializerMethodField("get_genre")
    country = serializers.SerializerMethodField("get_country")
    cast = serializers.SerializerMethodField("get_cast")
    writers = serializers.SerializerMethodField("get_writers")
    directors = serializers.SerializerMethodField("get_directors")
    collections = serializers.SerializerMethodField("get_collections")
    related = serializers.SerializerMethodField("get_related")
    suggestions = serializers.SerializerMethodField("get_suggestions")
    subtitles = serializers.SerializerMethodField("get_subtitles")

    class Meta:
        model = Movie
        fields = [
            "pk",
            "imdb_id",
            "uuid",
            "slug",
            "title",
            "fa_title",
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
            "url",
            "en_story",
            "fa_story",
            "franchise",
            "cast",
            "writers",
            "directors",
            "show_poster",
            "ultra",
            "published_at",
            "collections",
            "related",
            "suggestions",
            "subtitles",
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

    def get_collections(self, movie):
        return get_collection(movie)

    def get_subtitles(self, movie):
        subtitles_objs = Subtitle.objects.filter(video__movie=movie)
        return SubtitleSerializer(subtitles_objs, many=True).data

    def get_audios(self, movie):
        audios_objs = Audio.objects.filter(movie=movie)
        return AudioSerializer(audios_objs, many=True).data

    def get_related(self, movie):
        if movie.franchise is not None:
            movies = Movie.objects.filter(franchise=movie.franchise).exclude(
                uuid=movie.uuid
            )
            return [all_serializer(m) for m in movies]
        return []

    def get_suggestions(self, movie):
        all_genres = movie.genre.all()
        other_movies = (
            [movie for movie in Movie.objects.all().exclude(franchise=movie.franchise)]
            if movie.franchise is not None
            else [movie for movie in Movie.objects.all().exclude(uuid=movie.uuid)]
        )
        serials = [serial for serial in Serial.objects.all()]
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


class VideoSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField("get_file")

    class Meta:
        model = Video
        fields = ["file", "resolution", "size", "duration"]

    def get_file(self, video):
        return SERVER + video.file.url
