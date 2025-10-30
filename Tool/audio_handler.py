import os

from Movie.models import Movie, Video, Audio as MovieAudio
from Movie.values import get_movie_root
from Serial.models import Episode, Audio as EpisodeAudio
from Serial.values import get_serial_root


class AudioHandler:
    def __init__(self, obj):
        self.obj = obj
        self.done_audios = []

    def get_audios_folder(self):
        if self.obj is not None:
            if type(self.obj) == Movie:
                subs_folder = get_movie_root(self.obj, filepath='audios', use_media=True)
                if not os.path.isdir(subs_folder):
                    os.makedirs(subs_folder, exist_ok=True)
                return subs_folder
            elif type(self.obj) == Episode:
                subs_folder = get_serial_root(self.obj.serial, filepath=f'season-{self.obj.number}/audios',
                                              use_media=True)
                if not os.path.isdir(subs_folder):
                    os.makedirs(subs_folder, exist_ok=True)
                return subs_folder

    def get_video_path(self):
        if type(self.obj) == Movie:
            videos = Video.objects.filter(movie=self.obj)
            video = videos.first()
            return video.file.path
        elif type(self.obj) == Episode:
            return self.obj.video.path

    def run_command(self, fa_audio, en_audio, video_path):
        if not os.path.isfile(fa_audio):
            os.system(f'ffmpeg  -i "{video_path}" -map 0:a:0? -c copy "{fa_audio}"')
            if os.path.isfile(fa_audio):
                new_form = {'label': 'Persian', 'path_name': fa_audio.replace('media/', '')}
                self.done_audios.append(new_form)
        else:
            new_form = {'label': 'Persian', 'path_name': fa_audio.replace('media/', '')}
            self.done_audios.append(new_form)
        if not os.path.isfile(en_audio):
            os.system(f'ffmpeg  -i "{video_path}" -map 0:a:0? -c copy "{en_audio}"')
            if os.path.isfile(en_audio):
                new_form = {'label': 'English', 'path_name': en_audio.replace('media/', '')}
                self.done_audios.append(new_form)
        else:

            new_form = {'label': 'English', 'path_name': en_audio.replace('media/', '')}
            self.done_audios.append(new_form)

    def action(self):
        audios_folder = self.get_audios_folder()
        video_path = self.get_video_path()
        fa_audio_name = f"episode-{self.obj.number}-audio-fa.mp3" if type(self.obj) == Episode else "audio-fa.mp3"
        en_audio_name = f"episode-{self.obj.number}-audio-en.mp3" if type(self.obj) == Episode else "audio-en.mp3"
        en_audio = f'{audios_folder}/{en_audio_name}'
        fa_audio = f'{audios_folder}/{fa_audio_name}'
        self.run_command(fa_audio, en_audio, video_path)
        for audio in self.done_audios:
            audio_instance = MovieAudio.objects.create(movie=self.obj) if type(
                self.obj) == Movie else EpisodeAudio.objects.create(episode=self.obj)
            audio_instance.language = audio['label']
            audio_instance.file.name = audio["path_name"]
            audio_instance.save()
        return self.done_audios
