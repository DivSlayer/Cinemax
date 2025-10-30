import json

from django.conf import settings
from rest_framework import serializers

from Category.serializers import CategorySerializer
from Movie.models import Subtitle as MovieSubtitle, Audio as MovieAudio, Movie, Video, Audio
from Person.models import Person
from Serial.models import Serial, Episode, Audio as EpisodeAudio, EpisodeSubtitle

server = settings.SITE_URL.rstrip('/')


class SmallMovieSerializer(serializers.ModelSerializer):
    poster_img = serializers.SerializerMethodField("get_poster_img")
    item_img = serializers.SerializerMethodField("get_item_img")
    colors = serializers.SerializerMethodField("get_colors")
    genre = serializers.SerializerMethodField("get_genre")

    class Meta:
        model = Movie
        fields = [
            "pk",
            "slug",
            "imdb_id",
            "uuid",
            "slug",
            "title",
            "fa_title",
            "poster_img",
            "item_img",
            "colors",
            "url",
            "fa_story",
            "rating",
            "resolution",
            "genre",
        ]

    def get_poster_img(self, movie):
        if movie.poster_img:
            return server + movie.poster_img.url
        return None

    def get_item_img(self, movie):
        if movie.compress_img:
            return server + movie.compress_img.url
        return None

    def get_colors(self, movie):
        colors = [f"{movie.second_color}", f"{movie.third_color}"]
        return colors

    def get_genre(self, movie):
        return CategorySerializer(movie.genre.all(), many=True).data


class SmallSerialSerializer(serializers.ModelSerializer):
    poster_img = serializers.SerializerMethodField("get_poster_img")
    item_img = serializers.SerializerMethodField("get_item_img")
    colors = serializers.SerializerMethodField("get_colors")
    genre = serializers.SerializerMethodField("get_genre")

    class Meta:
        model = Serial
        fields = [
            "pk",
            "slug",
            "imdb_id",
            "uuid",
            "title",
            "fa_title",
            "poster_img",
            "colors",
            "item_img",
            "url",
            "fa_story",
            "rating",
            "resolution",
            "genre",
        ]

    def get_poster_img(self, serial):
        if serial.poster_img:
            return server + serial.poster_img.url
        return None

    def get_item_img(self, serial):
        print(serial.compress_img)
        if serial.compress_img:
            return server + serial.compress_img.url
        return None

    def get_colors(self, movie):
        colors = [f"{movie.second_color}", f"{movie.third_color}"]
        return colors

    def get_genre(self, movie):
        return CategorySerializer(movie.genre.all(), many=True).data


class SmallPersonSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField("get_img")

    class Meta:
        model = Person
        fields = [
            "imdb_id",
            "slug",
            "name",
            "img",
            "height",
            "birth_date",
            "age",
            "bio",
            "url",
        ]

    def get_img(self, person):
        return server + person.img.url if person.img else None


class SubtitleSerializer(serializers.ModelSerializer):
    vtt = serializers.SerializerMethodField("get_vtt")
    srt = serializers.SerializerMethodField("get_srt")

    class Meta:
        model = MovieSubtitle
        fields = ["vtt", "srt", "language"]

    def get_vtt(self, subtitle):
        return server + subtitle.vtt.url if subtitle.vtt else None

    def get_srt(self, subtitle):
        return server + subtitle.srt.url


class AudioSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField("get_label")
    stream_url = serializers.SerializerMethodField("get_stream_url")

    class Meta:
        model = MovieAudio
        fields = ["label", "stream_url"]

    def get_label(self, audio):
        return audio.language

    def get_stream_url(self, audio):
        return server + audio.file.url


def get_collection(movie: Movie, vitals=False):
    videos = Video.objects.filter(movie=movie)
    datas = []
    print(f"server is :{server}")
    for video in videos:
        new_dict = {
            "uuid": video.uuid,
            "label": video.resolution,
            "title": video.resolution,

            "resolution": video.resolution,
            "size": video.size,
            "sizeb": int(video.sizeb),
            "subbed": video.subbed,
            "dubbed": video.dubbed,
        }
        if vitals:
            new_dict["censors"] = json.loads(video.censors)
            new_dict["credits"] = json.loads(video.credits)
            new_dict["audios"] = AudioSerializer(
                MovieAudio.objects.filter(movie=movie), many=True
            ).data
            new_dict["subtitles"] = SubtitleSerializer(
                MovieSubtitle.objects.filter(movie=movie), many=True
            ).data
            new_dict["stream_url"] = server + video
        datas.append(
            new_dict
        )
    return datas


class GetSourceSerializer:
    def __init__(self, obj,user):
        self.obj = obj
        self.stream_url = None
        self.download_url = None
        self.credits = None
        self.censors = None
        self.subtitles = None
        self.audios = None
        self.user = user

    def serialize(self):
        if type(self.obj) == Video:
            movie = self.obj.movie
            stream_url = self.get_stream_url()
            if stream_url is not None:
                self.stream_url = server + stream_url
            
            download_url = self.get_download_url()
            if download_url is not None:
                self.download_url = server + download_url
            
            self.censors = json.loads(self.obj.censors)
            self.credits = json.loads(self.obj.credits)
            self.audios = Audio.objects.filter(movie=movie)
            self.audios = AudioSerializer(self.audios, many=True).data
            self.subtitles = MovieSubtitle.objects.filter(video=self.obj)
            self.subtitles = SubtitleSerializer(self.subtitles, many=True).data
            return {
                "uuid": self.obj.uuid,
                "stream_url": server+ self.obj.file.url,
                "download_url": server + self.obj.file.url,
                "censors": self.censors,
                "credits": self.credits,
                "audios": self.audios,
                "subtitles": self.subtitles,
                "has_intro":self.obj.has_intro,
                'subbed': self.obj.subbed,
                'dubbed': self.obj.dubbed,
                'resolution': self.obj.resolution,
                'status':self.obj.status,
            }
        elif type(self.obj) == Episode:
            stream_url = self.get_stream_url()
            if stream_url is not None:
                self.stream_url = server + stream_url
            
            download_url = self.get_download_url()
            if download_url is not None:
                self.download_url = server + download_url
            
            audios = EpisodeAudio.objects.filter(episode=self.obj)
            audios = AudioSerializer(audios, many=True).data
            subtitles = EpisodeSubtitle.objects.filter(episode=self.obj)
            subtitles = SubtitleSerializer(subtitles, many=True).data
            self.censors = json.loads(self.obj.censors)
            self.credits = json.loads(self.obj.credits)
            self.audios = audios
            self.subtitles = subtitles
            return {
                "stream_url": server+self.obj.video.url,
                "download_url": server+self.obj.video.url,
                "censors": self.censors,
                "credits": self.credits,
                "audios": self.audios,
                "subtitles": self.subtitles,
            }


    def get_stream_url(self):
        """Generate temporary signed URL for streaming"""
        # Check user subscription
        sub_condition = False
        if self.user.plan is not None and self.user.plan.play_available:
            sub_condition = True
        if not sub_condition:
            return None

        return f"/api/stream/{self.obj.uuid}"


    def get_download_url(self):
        """Generate temporary signed URL for streaming"""
        # Check user subscription
        sub_condition = False
        if self.user.plan is not None and self.user.plan.download_available:
            sub_condition = True
        if not sub_condition:
            
            return None

        return f"/api/download/{self.obj.uuid}"
