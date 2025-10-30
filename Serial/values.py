from Utility.views import get_safe_words


def get_serial_root(serial, filepath=None, use_media=False):
    main_folder = 'media/serials' if use_media else 'serials'
    title = get_safe_words(serial.title)
    path = f'{main_folder}/{title}-{serial.uuid}/{filepath}' if filepath is not None else f'{main_folder}/{title}-{serial.uuid}/'
    return path


def get_episode_path(episode):
    return get_serial_root(episode.serial, filepath=f'season-{episode.season.number}/episodes')
