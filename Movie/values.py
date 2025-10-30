
from Utility.views import get_safe_words


def get_movie_root(movie, filepath=None, use_media=False):
    main_folder = 'media/movies' if use_media else 'movies'
    title = get_safe_words(movie.title)
    path = f'{main_folder}/{title}-{movie.uuid}/{filepath}' if filepath is not None else f'{main_folder}/{title}-{movie.uuid}/'
    return path
