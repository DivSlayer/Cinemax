from Country.models import Country
from Movie.models import Movie, Audio, Subtitle as MovieSubtitle
from Serial.models import Serial
import pandas as pd


def adv_search_filter(request, movies):
    data_type = request.GET.get("type", None)
    directors = request.GET.get("director", None)
    countries = request.GET.get("countries", None)
    genres = request.GET.get("genres", None)
    genres = (
        [str(genre).strip() for genre in genres.split(",")]
        if genres is not None
        else None
    )
    directors = (
        [str(director).strip() for director in directors.split(",")]
        if directors is not None
        else None
    )
    actors = request.GET.get("actors", None)
    actors = (
        [str(actor).strip() for actor in actors.split(",")]
        if actors is not None
        else None
    )
    resolution = request.GET.get("resolution", None)
    year_max = request.GET.get("year-max", None)
    year_max = (
        int(year_max) / 100 * (2023 - 1945) + 1945 if year_max is not None else None
    )
    year_min = request.GET.get("year-min", None)
    year_min = (
        2023 - int(year_min) / 100 * (2023 - 1945) if year_min is not None else None
    )
    rate_max = request.GET.get("rate-max", None)
    rate_max = int(rate_max) / 100 * 10 if rate_max is not None else None
    rate_min = request.GET.get("rate-min", None)
    rate_min = int(rate_min) / 100 * 10 if rate_min is not None else None
    subbed = request.GET.get("subbed", None)
    subbed = True if subbed == "on" else False
    dubbed = request.GET.get("dubbed", None)
    dubbed = True if dubbed == "on" else False

    if data_type is not None:
        if data_type == "movie":
            if type(movies[0]) != Movie:
                return []
        elif data_type == "series":
            if type(movies[0]) != Serial:
                return []
        else:
            return []
    if countries is not None:
        countries = countries.split(",")
        cs = []
        for c in countries:
            if c != "" or c is not None:
                c_ins = Country.objects.get(name=c)
                cs.append(c_ins.name)
        movies = movies.filter(country__name__in=cs)
    if type(movies.first()) == Movie:
        if resolution is not None:
            movies = movies.filter(resolution=resolution)
    else:
        if resolution is not None:
            return []
    if subbed:
        new_list = []
        if type(movies[0]) == Movie:
            for movie in movies:
                if len(MovieSubtitle.objects.filter(movie=movie)) > 0:
                    new_list.append(movie)
        else:
            return []
        movies = new_list
    if dubbed:
        new_list = []
        if type(movies[0]) == Movie:
            for movie in movies:
                if len(Audio.objects.filter(movie=movie)) > 0:
                    new_list.append(movie)
        else:
            return []
        movies = new_list
    if directors is not None:
        movies = movies.filter(directors__name__in=directors)
    if genres is not None:
        new_list2 = []
        for movie in movies:
            isin = True
            for genre in genres:
                if genre not in [genre.en_title for genre in movie.genre.all()]:
                    isin = False
            if isin:
                new_list2.append(movie)
        movies = new_list2
        # movies = movies.filter(cast__name__in=actors)
    if actors is not None:
        new_list2 = []
        for movie in movies:
            isin = True
            for actor in actors:
                if actor not in [cast.name for cast in movie.cast.all()]:
                    isin = False
            if isin:
                new_list2.append(movie)
        movies = new_list2
        # movies = movies.filter(cast__name__in=actors)
    if year_max is not None:
        new_list = []
        for movie in movies:
            if movie.year is not None:
                if float(movie.year) < year_max:
                    new_list.append(movie)
        movies = new_list
    if year_min is not None:
        new_list = []
        for movie in movies:
            if movie.year is not None:
                if float(movie.year) > year_min:
                    new_list.append(movie)
        movies = new_list
    if rate_max is not None:
        new_list = []
        for movie in movies:
            if movie.rating is not None:
                if float(movie.rating) < rate_max:
                    new_list.append(movie)
        movies = new_list
    if rate_min is not None:
        new_list = []
        for movie in movies:
            if movie.rating is not None:
                if float(movie.rating) > year_min:
                    new_list.append(movie)
        movies = new_list
    return movies


def ordering(arr, order=None):
    ratings = []
    if order is not None:
        if order.split("-")[len(order.split("-")) - 1] == "title":
            ratings = [movie.title for movie in arr]
        if order.split("-")[len(order.split("-")) - 1] == "published_at":
            ratings = [movie.published_at for movie in arr]
        if order.split("-")[len(order.split("-")) - 1] == "rating":
            ratings = [movie.rating for movie in arr]
        if order.split("-")[len(order.split("-")) - 1] == "year":
            ratings = [movie.year for movie in arr]
        if order.split("-")[len(order.split("-")) - 1] == "release_date":
            ratings = [movie.release_date for movie in arr]
    else:
        ratings = [movie.rating for movie in arr]
    print(f"order: {order} ratings length: {len(ratings)} arr length: {len(arr)}")
    df = pd.DataFrame({"Movie": arr, "Per": ratings})
    if order is not None:
        df = df.sort_values(
            by="Per", ascending=False if len(order.split("-")) - 1 > 0 else True
        )
    else:
        df = df.sort_values(by="Per", ascending=False)
    arr = df[["Movie"]].to_numpy()
    return [movie[0] for movie in arr]
