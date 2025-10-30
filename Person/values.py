from Utility.views import get_safe_words


def get_person_root(person, filepath=None, use_media=False):
    main_folder = 'media/persons' if use_media else 'persons'
    title = get_safe_words(person.name)
    path = f'{main_folder}/{title}-{person.imdb_id}/{filepath}' if filepath is not None else f'{main_folder}/{title}-{person.imdb_id}/'
    return path
