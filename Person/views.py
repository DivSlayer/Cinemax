from django.shortcuts import render

from Movie.models import Movie
from Person.models import Person
from Serial.models import Serial
from Utility.responses import error_response, list_response
from Utility.tools import ordering
from Person.serializers import get_serials, get_movies


# Create your views here.
def index(request, slug):
    person = Person.objects.filter(slug=slug)
    order = request.GET.get('order', '-rating')
    page = request.GET.get('page', 1)
    page = int(page)
    if len(person) != 0:
        person = person.first()
        movies = []
        serials = []
        for movie in Movie.objects.all():
            if person in movie.cast.all():
                if movie not in movies:
                    movies.append(movie)
            if person in movie.writers.all():
                if movie not in movies:
                    movies.append(movie)
            if person in movie.directors.all():
                if movie not in movies:
                    movies.append(movie)
        for serial in Serial.objects.all():
            if person in serial.cast.all():
                if serial not in serials:
                    serials.append(serial)
            if person in serial.writers.all():
                if serial not in serials:
                    serials.append(serial)
            if person in serial.directors.all():
                if serial not in serials:
                    serials.append(serial)
        together = []
        together.extend(movies)
        together.extend(serials)
        first_int = (page - 1) * 20
        last_int = page * 20
        ordered = ordering(together, order)
        context = {"person": person, 'movies': ordered[first_int:last_int]}
        return render(request, 'person.html', context=context)
    else:
        return error_response("Person not found!", 404)


def person_movies(request):
    all_together = []
    uuid = request.GET.get('id', None)
    person = Person.objects.get(imdb_id=uuid)
    movies = get_movies(person)
    serials = get_serials(person)
    all_together.extend(movies)
    all_together.extend(serials)
    order = request.GET.get("order", None)
    ordered = ordering(all_together, order)
    return list_response(arr=ordered)
