import math

from django.shortcuts import render
from Utility.responses import error_response, list_response
from Category.models import Category
from Movie.models import Movie
from Serial.models import Serial
from Utility.tools import ordering


def movies(request, title):
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


def index(request, title):
    all_together = []
    category = Category.objects.get(en_title=title)
    page = request.GET.get('page', 1)
    order = request.GET.get('order', '-rating')
    page = int(page)
    movies_list = [movie for movie in Movie.objects.filter(genre__en_title__in=[category.en_title])]
    serials = [serial for serial in Serial.objects.filter(genre__en_title__in=[category.en_title])]
    all_together.extend(movies_list)
    all_together.extend(serials)
    ordered = ordering(all_together, order=order)
    first_int = (page - 1) * 20
    last_int = page * 20
    main_list = ordered[first_int:last_int]
    context = {
        'category': category,
        'movies': main_list, 'page': page,
        'last_page': math.ceil(len(ordered) / 20),
        'first_page': 1, }
    return render(request, 'category.html', context=context)
