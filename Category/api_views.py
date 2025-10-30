import json

from django.http import HttpResponse

from Category.models import Category
from Cinemax.env import Env
from Movie.models import Movie
from Serial.models import Serial
from Utility.responses import list_response
from Utility.tools import ordering

SERVER = Env().get_server()


def single(request, title):
    genre = Category.objects.get(en_title=title)
    cat = genre.en_title
    page = request.GET.get('page', 1)
    page = int(page)
    all_together = []
    movies = [movie for movie in Movie.objects.filter(genre__en_title__in=[cat])]
    serials = [serial for serial in Serial.objects.filter(genre__en_title__in=[cat])]
    all_together.extend(movies)
    all_together.extend(serials)
    order = request.GET.get("order", None)
    ordered = ordering(all_together, order)
    return list_response(arr=ordered, small=True, page=page)


def list_genre(request):
    categories = Category.objects.all()
    datas = []
    for cat in categories:
        movies = list(Movie.objects.filter(genre__en_title__in=[cat.en_title]))
        serials = list(Movie.objects.filter(genre__en_title__in=[cat.en_title]))
        all_together = []
        all_together.extend(movies)
        all_together.extend(serials)
        ordered = ordering(all_together)
        best_one = set_best(ordered)
        new_form = {
            'fa_title': cat.fa_title,
            'en_title': cat.en_title,
            'poster': SERVER + best_one.poster_img.url if best_one is not None else None,
            'icon' : cat.icon
        }
        datas.append(new_form)
    return HttpResponse(json.dumps(datas), content_type='application/json')


def set_best(arr, current=0):
    print(
        f"current: {current}, length: {len(arr)}, cond: {len(arr) > (current - 1)}, p: {arr[current].poster_img.url if arr[current].poster_img else None}")
    if len(arr) > (current - 1):
        if arr[current].poster_img:
            return arr[current]
        else:
            return set_best(arr, current + 1)
    else:
        return None
