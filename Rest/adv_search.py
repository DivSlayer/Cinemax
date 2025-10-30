import json
from django.http import HttpResponse

from Category.models import Category
from Country.models import Country
from Movie.models import Movie, Video, Subtitle, Audio
from Person.models import Person
from Serial.models import Serial
from Utility.responses import list_response
from Utility.tools import ordering


def advanced_search(request):
    all_together = []
    movies = Movie.objects.all()
    serials = Serial.objects.all()
    page = request.POST.get('page', 1)
    defaults = {
        "actors": None,
        "categories": ["0"],
        "countries": ["0"],
        "resolution": ["0"],
        "directors": None,
        "censored": False,
        "dubbed": False,
        "subbed": False,
        "rate_max": 10,
        "rate_min": 1,
        "year_max": int(Movie.objects.all().order_by("-year").first().year),
        "year_min": int(Movie.objects.all().order_by("year").first().year),
    }
    functions = {"actors": filter_actors, "directors": filter_directors, "categories": filter_categories,
                 "countries": filter_countries,
                 "censored": filter_censored, "dubbed": filter_dubbed, "subbed": filter_subbed,
                 "rate_max": filter_rate_max, "rate_min": filter_rate_min, "year_max": filter_year_max,
                 "year_min": filter_year_min,"resolution" :filter_resolution}
    queries = {}
    for key in defaults.keys():
        value = defaults[key]
        value = request.POST.get(key, value)
        value = value.strip() if type(value) == str else value
        if value != "" and defaults[key] != value:
            value = json.loads(value)
        queries[key] = value
    print(queries)
    for key, value in queries.items():
        if value != defaults[key]:
            print(f"{key} is diffenret new: {value} default: {defaults[key]}")
            movies, serials = functions[key](movies, serials, value)
    movies = [m for m in movies]
    serials = [s for s in serials]
    all_together.extend(movies)
    all_together.extend(serials)
    all_together = ordering(all_together, json.loads(request.POST.get('order', '-rating')))
    return list_response(all_together, page=page,per_page=len(all_together) if len(all_together) > 0 else 1,)


def filter_actors(movies, serials, value):
    return person_filter(movies, serials, value, type_o="actor")


def filter_directors(movies, serials, value):
    return person_filter(movies, serials, value, type_o="director")


def person_filter(movies, serials, value, type_o):
    actors = value.split(",")
    actors = [actor.strip() for actor in actors]
    actors_ins = []
    for name in actors:
        find = Person.objects.filter(name=name)
        if len(find) > 0:
            actors_ins.append(find.first().name)
        else:
            actors_ins.append(None)
    if type_o == "actor":
        for name in actors_ins:
            movies = movies.filter(cast__name__in=[name])
            serials = serials.filter(cast__name__in=[name])
    if type_o == "director":
        for name in actors_ins:
            movies = movies.filter(directors__name__in=[name])
            serials = serials.filter(directors__name__in=[name])
    return movies, serials


def filter_categories(movies, serials, value):
    for cat in value:
        cat_ins = Category.objects.filter(en_title=cat)
        if len(cat_ins) > 0:
            cat_ins = cat_ins.first()
            movies = movies.filter(genre__en_title__in=[cat_ins.en_title])
            serials = serials.filter(genre__en_title__in=[cat_ins.en_title])
        else:
            movies = movies.filter(genre__en_title__in=[])
            serials = serials.filter(genre__en_title__in=[])
    return movies, serials


def filter_countries(movies, serials, value):
    for country in value:
        cat_ins = Country.objects.filter(name=country)
        if len(cat_ins) > 0:
            cat_ins = cat_ins.first()
            movies = movies.filter(country__name__in=[cat_ins.name])
            serials = serials.filter(country__name__in=[cat_ins.name])
        else:
            movies = movies.filter(country__name__in=[])
            serials = serials.filter(country__name__in=[])
    return movies, serials


def filter_censored(movies, serials, value):
    new_list = []
    for movie in movies:
        videos = Video.objects.filter(movie=movie)
        censored = False
        for video in videos:
            censored_json = json.loads(video.censors)
            if type(censored_json) == list and len(censored_json) > 0:
                censored = True
        if censored:
            new_list.append(movie)
    return new_list, []

def filter_resolution(movies, serials, value):
    new_list = []
    new_list_s=[]
    print(value)
    for movie in movies:
        videos = Video.objects.filter(movie=movie)
        for video in videos:
            if video.resolution in value:
                new_list.append(movie)
    for serial in serials:
        if serial.resolution in value:
            new_list_s.append(serial)
    return new_list, []


def filter_subbed(movies, serials, value):
    new_list = []
    for movie in movies:
        subs = Subtitle.objects.filter(movie=movie)
        if len(subs) > 0:
            new_list.append(movie)
    return new_list, []


def filter_dubbed(movies, serials, value):
    new_list = []
    for movie in movies:
        audios = Audio.objects.filter(movie=movie)
        if len(audios) > 0:
            new_list.append(movie)
    return new_list, []


def filter_year_max(movies, serials, value):
    new_list_m = []
    new_list_s = []
    for movie in movies:
        if movie.year:
            rate = float(movie.year)
            if rate <= value:
                new_list_m.append(movie)
    for movie in serials:
        if movie.year:
            rate = float(movie.year)
            if rate <= value:
                new_list_s.append(movie)
    return new_list_m, new_list_s


def filter_year_min(movies, serials, value):
    new_list_m = []
    new_list_s = []
    for movie in movies:
        if movie.year:
            rate = float(movie.year)
            if rate >= value:
                new_list_m.append(movie)
    for movie in serials:
        if movie.year:
            rate = float(movie.year)
            if rate >= value:
                new_list_s.append(movie)
    return new_list_m, new_list_s


def filter_rate_max(movies, serials, value):
    new_list_m = []
    new_list_s = []
    for movie in movies:
        if movie.rating:
            rate = float(movie.rating)
            if rate <= value:
                new_list_m.append(movie)
    for movie in serials:
        if movie.rating:
            rate = float(movie.rating)
            if rate <= value:
                new_list_s.append(movie)
    return new_list_m, new_list_s


def filter_rate_min(movies, serials, value):
    new_list_m = []
    new_list_s = []
    for movie in movies:
        if movie.rating:
            rate = float(movie.rating)
            if rate >= value:
                new_list_m.append(movie)
    for movie in serials:
        if movie.rating:
            rate = float(movie.rating)
            if rate >= value:
                new_list_s.append(movie)
    return new_list_m, new_list_s
