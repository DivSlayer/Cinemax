import json
from django.http import HttpResponse
from django.shortcuts import render
from Movie.models import Movie, Subtitle as MovieSubtitle
from Serial.models import Season
from Utility.no_serializer import all_serializer, get_object


def online(request, uuid):
    try:
        movie = get_object(uuid, use_imdb=False)
        if type(movie) == Season:
            title = ("سریال " + str(movie.serial.title) + "فصل " +
                     str(movie.number))
        else:
            title = movie.title
        context = {
            "movie": movie,
            'title': title,
            "poster": movie.poster_img.url if type(movie) == Movie else movie.serial.poster_img.url,
        }
        return render(request, "player/player.html", context)
    except Exception as e:
        raise e
        return HttpResponse(f"Page not found! {uuid}", status=404)


def online_details(request, uuid):
    obj = get_object(uuid, use_imdb=False)
    serialized = all_serializer(obj)
    return HttpResponse(json.dumps(serialized), content_type="application/json", charset="utf-8")
