from django.shortcuts import render

from Movie.models import Movie, Subtitle, Audio, Video, Trailer
from Serial.models import Serial
from Utility.responses import error_response

def get_related(movie):
    if movie.franchise is not None:
        movies = Movie.objects.filter(franchise=movie.franchise).exclude(uuid=movie.uuid)
        return movies
    return []


def get_suggestions(movie):
    all_genres = movie.genre.all()
    other_movies = [movie for movie in
                    Movie.objects.all().exclude(franchise=movie.franchise)] if movie.franchise is not None else [
        movie for movie in Movie.objects.all().exclude(uuid=movie.uuid)]
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
    return together[:5]


def single(request, slug):
    movie = Movie.objects.filter(slug=slug)
    if len(movie) != 0:
        movie = movie.first()
        suggestions = get_suggestions(movie)
        related = get_related(movie)
        subbed = len(Subtitle.objects.filter(movie=movie)) > 0
        dubbed = len(Audio.objects.filter(movie=movie)) > 0
        context = {
            "movie": movie,
            'suggestions': suggestions,
            'related': related,
            'subbed': subbed,
            'dubbed': dubbed,
            'videos': Video.objects.filter(movie=movie),
            'subtitles': Subtitle.objects.filter(movie=movie),
            'trailers': Trailer.objects.filter(movie=movie)
        }
        return render(request, 'test/index.html', context=context)
    else:
        return error_response("Movie not found!", 404)
