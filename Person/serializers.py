from rest_framework import serializers
from Cinemax.env import Env
from Movie.models import Movie
from Person.models import Person
from Rest.common_serializers import SmallMovieSerializer, SmallSerialSerializer
from Serial.models import Serial

SERVER = Env().get_server()


class PersonSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField("get_img")
    movies = serializers.SerializerMethodField("get_movies")
    serials = serializers.SerializerMethodField("get_serials")

    class Meta:
        model = Person
        fields = [
            "imdb_id",
            "slug",
            "name",
            "img",
            "height",
            "birth_date",
            "age",
            "bio",
            "movies",
            "serials",
            "url",
        ]

    def get_img(self, person):
        return SERVER + person.img.url if person.img else None

    def get_movies(self, person):
        all_together = []
        acted_in = Movie.objects.filter(cast__name__in=[person.name])
        directed = Movie.objects.filter(directors__name__in=[person.name])
        written = Movie.objects.filter(writers__name__in=[person.name])

        for movie in acted_in:
            all_together.append(movie)

        for movie in directed:
            if movie not in all_together:
                all_together.append(movie)

        for movie in written:
            if movie not in all_together:
                all_together.append(movie)
        return [SmallMovieSerializer(movie).data for movie in all_together]

    def get_serials(self, person):
        all_together = []
        acted_in = Serial.objects.filter(cast__name__in=[person.name])
        directed = Serial.objects.filter(directors__name__in=[person.name])
        written = Serial.objects.filter(writers__name__in=[person.name])
        for serial in acted_in:
            all_together.append(serial)

        for serial in directed:
            if serial not in all_together:
                all_together.append(serial)

        for serial in written:
            if serial not in all_together:
                all_together.append(serial)
        return [SmallSerialSerializer(serial).data for serial in all_together]


def get_movies(person):
    all_together = []
    acted_in = Movie.objects.filter(cast__name__in=[person.name])
    directed = Movie.objects.filter(directors__name__in=[person.name])
    written = Movie.objects.filter(writers__name__in=[person.name])

    for movie in acted_in:
        all_together.append(movie)

    for movie in directed:
        if movie not in all_together:
            all_together.append(movie)

    for movie in written:
        if movie not in all_together:
            all_together.append(movie)
    return all_together


def get_serials(person):
    all_together = []
    acted_in = Serial.objects.filter(cast__name__in=[person.name])
    directed = Serial.objects.filter(directors__name__in=[person.name])
    written = Serial.objects.filter(writers__name__in=[person.name])
    for serial in acted_in:
        all_together.append(serial)

    for serial in directed:
        if serial not in all_together:
            all_together.append(serial)

    for serial in written:
        if serial not in all_together:
            all_together.append(serial)
    return all_together


class ExportPersonSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField("get_img")

    class Meta:
        model = Person
        fields = [
            "imdb_id",
            "slug",
            "name",
            "img",
            "height",
            "birth_date",
            "age",
            "bio",
            "url",
        ]

    def get_img(self, person):
        return person.img.name if person.img else None

    def create(self, validate_data):
        person = Person(
            imdb_id=validate_data["imdb_id"],
            slug=validate_data["slug"],
            name=validate_data["name"],
            height=validate_data["height"],
            birth_date=validate_data["birth_date"],
            age=validate_data["age"],
            bio=validate_data["bio"],
            url=validate_data["url"],
        )
        person.save()
