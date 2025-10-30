import os
import re
import shutil
from itertools import combinations

import environ
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext as _
from Category.models import Category
from Country.models import Country
from Person.models import Person
from Serial.values import get_serial_root
from Tag.models import Tag
from Utility.views import (
    Video_Validator,
    get_duration,
    get_resolution,
    get_size,
    get_uuid,
    Image_Validator, get_sub_audio_nums,
)
from django.db.models.signals import post_save


def get_safe_words(string, capitalize=False):
    list_words = []
    for word in string.strip().split(" "):
        check = re.match(r"[0-9A-Za-z]", word)
        if check is not None:
            list_words.append(check.string.lower())
    input_string = " ".join(list_words)
    input_string = input_string.encode("latin", "ignore")
    input_string = input_string.decode("utf-8", "ignore")
    input_string = input_string.replace("'", "")
    input_string = input_string.replace(":", "").lower()
    if capitalize:
        input_string = " ".join([word.capitalize() for word in input_string.split(" ")])
    return input_string


def get_poster_path(self, filename):
    return get_serial_root(self, "poster.jpg")


def get_item_path(self, filename):
    return get_serial_root(self, "item_img.jpg")


def get_compress_path(movie, filename):
    return get_serial_root(movie, "compress_img.jpg")


class Serial(models.Model):
    imdb_id = models.CharField(max_length=100, blank=True, null=True)
    uuid = models.CharField(max_length=10, default=get_uuid, unique=True)
    slug = models.SlugField(max_length=300, blank=True, null=True)
    title = models.CharField(max_length=300)
    fa_title = models.CharField(max_length=300, blank=True, null=True)
    poster_img = models.FileField(
        upload_to=get_poster_path, validators=Image_Validator, null=True, blank=True
    )
    item_img = models.FileField(
        upload_to=get_item_path, validators=Image_Validator, null=True, blank=True
    )
    compress_img = models.FileField(
        upload_to=get_compress_path, validators=Image_Validator, null=True, blank=True
    )
    rating = models.CharField(max_length=50, blank=True, null=True)
    year = models.CharField(max_length=50, blank=True, null=True)
    genre = models.ManyToManyField(Category, blank=True)
    language = models.CharField(max_length=300, blank=True, null=True)
    country = models.ManyToManyField(Country, blank=True)
    budget = models.CharField(max_length=300, blank=True, null=True)
    certificate = models.CharField(max_length=300, blank=True, null=True)
    resolution = models.CharField(max_length=300, blank=True, null=True)
    duration = models.CharField(max_length=300, blank=True, null=True)
    quotes = models.TextField(blank=True)
    en_story = models.TextField(blank=True)
    fa_story = models.TextField(blank=True)
    cast = models.ManyToManyField(Person, blank=True, related_name="serial_cast")
    writers = models.ManyToManyField(Person, blank=True, related_name="serial_writers")
    directors = models.ManyToManyField(
        Person, blank=True, related_name="serial_directors"
    )
    show_poster = models.BooleanField(default=True)
    ultra = models.BooleanField(default=False)
    qrCode = models.TextField(null=True, blank=True)
    second_color = models.TextField(null=True, blank=True)
    third_color = models.TextField(null=True, blank=True)
    freq_color = models.TextField(null=True, blank=True)
    published_at = models.DateTimeField(
        auto_now=False, auto_now_add=True, blank=True, null=True
    )
    url = models.CharField(max_length=1000, null=True, blank=True)
    release_date = models.DateField(
        null=True, blank=True, auto_now_add=False, auto_now=False
    )
    tags = models.ManyToManyField(Tag, related_name="serial_tags", blank=True)

    def __str__(self):
        return self.title + "-" + self.uuid

    class Meta:
        ordering = ("-published_at",)


@receiver(pre_save, sender=Serial)
def my_callback(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.title)
    instance.url = f"/serial/{slugify(instance.title)}"


class Season(models.Model):
    uuid = models.CharField(
        default=get_uuid, max_length=10, unique=True, editable=False
    )
    serial = models.ForeignKey(Serial, on_delete=models.CASCADE)
    number = models.IntegerField()

    def __str__(self):
        return f"{self.serial}-season-{self.number}"


def get_video_path(self, filename):
    return get_serial_root(
        self.serial, f"episodes/season-{self.season.number}/" + filename
    )


class Episode(models.Model):
    uuid = models.CharField(
        default=get_uuid, max_length=10, unique=True, editable=False
    )
    number = models.IntegerField()
    duration = models.CharField(max_length=250, null=True, blank=True)
    size = models.CharField(max_length=250, null=True, blank=True)
    sizeb = models.CharField(max_length=250, null=True, blank=True)
    resolution = models.CharField(max_length=250, null=True, blank=True)
    serial = models.ForeignKey(
        Serial, on_delete=models.CASCADE, verbose_name=_("سریال")
    )
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name=_("فصل"))
    video = models.FileField(
        upload_to=get_video_path, validators=Video_Validator, verbose_name=_("ویدیو")
    )
    subbed = models.BooleanField(default=False)
    dubbed = models.BooleanField(default=False)
    censors = models.TextField(blank=True, null=True, default="[]")
    credits = models.TextField(blank=True, null=True, default="[]")
    published_at = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return (
                self.serial.title
                + "-season"
                + str(self.season.number)
                + "-episode"
                + str(self.number)
                + "-"
                + self.uuid
        )

    class Meta:
        ordering = ("serial", "number")

    def repair_name(self, filename):
        if os.path.isfile(self.video.path):
            res = get_resolution(self.video.path)
            size = get_size(self.video.path)
            sizeb = get_size(self.video.path, bytes=True)
            duration = get_duration(self.video.path)
            self.resolution = res
            self.size = size
            self.sizeb = sizeb
            self.duration = duration
            old_name = self.video.name
            old_path = f"media/{old_name}"
            new_name = get_video_name(self, filename, res)
            new_path = get_serial_root(
                self.serial,
                f"episodes/season-{self.season.number}/{new_name}",
                use_media=True,
            )
            if old_path != new_path:
                shutil.move(old_path, new_path)
            self.video.name = get_serial_root(
                self.serial, f"episodes/season-{self.season.number}/{new_name}"
            )
            self.save()
            return f"{self} Done!"
        return f"{self} error!"

    def add_tag(self):
        if os.path.isfile(self.video.path):
            ext = self.video.name.split(".")[-1]
            output_vid = f'media/{"/".join(self.video.name.split("/")[:-1])}/tagged.mkv'
            output_vid = os.path.join(os.getcwd(), output_vid)
            with open(output_vid, "w") as f:
                pass
            sub_num, audio_num = get_sub_audio_nums(
                self.video.path,
                root_folder=f'media/{"/".join(self.video.name.split("/")[:-1])}',
            )
            sub_string = ""
            audio_string = ""
            for i in range(0, sub_num):
                sub_string += f' -metadata:s:s:{i} title="Persian - Cinemax.com" -metadata:s:s:{i} language="Persian"'
            for i in range(0, audio_num):
                audio_string += f' -metadata:s:a:{i} title="Persian - Cinemax.com" -metadata:s:a:{i} language="Persian"'
            command = f'ffmpeg -i "{self.video.path}" -metadata title="{self.serial.title} Season {self.season.number} Episode {self.number} {self.resolution} - Cinemax.com" -codec copy -c:v copy -c:a copy -c:s copy  -metadata:s:v:0 title="Cinemax.com"  -metadata:s:v:0 handler="Cinemax.com" -metadata:s:v:0 comment="Cinemax.com" {sub_string} {audio_string} -y "{output_vid}"'
            value = os.system(command)
            if value == 0 and os.path.isfile(output_vid):
                path = self.video.path
                os.remove(self.video.path)
                shutil.move(output_vid, path)
                return True
            else:
                if os.path.isfile(output_vid):
                    os.remove(output_vid)
                return f"value: {value}, outputExist: {os.path.isfile(output_vid)}"
        else:
            return "file doesn't exist"


def get_array(string):
    all_combinations = []
    for i in range(1, len(string)):
        coms = combinations(string.lower().split(" "), i)
        for com in coms:
            all_combinations.append(" ".join(com))
    return all_combinations


def get_video_name(episode: Episode, old_name, res=None):
    file_name = ".".join(old_name.split(".")[:-1])
    ext = old_name.split(".")[-1]
    combs = get_array(episode.serial.title)
    combs.extend(slugify(episode.serial.title).split("-"))
    sites = settings.env.list("IMPORT_SITES", default=[])
    reses = ["2160p", "1080p", "720p", "480p", "360p", "240p"]
    extra_infos = []
    number = (
        f"E0{episode.number}" if len(str(episode.number)) == 1 else f"E{episode.number}"
    )
    s_number = (
        f"S0{episode.season.number}"
        if len(str(episode.season.number)) == 1
        else f"S{episode.season.number}"
    )
    extras = file_name.split(".")
    if not len(extras) > 1:
        extras = file_name.split("_")
    for word in extras:
        if (
                word.lower() not in combs
                and word.lower() not in reses
                and word.lower() != "cinemax"
                and word.lower() != f"{s_number}{number}".lower()
                and word.lower() not in sites
        ):
            extra_infos.append(word)
    safe_words = " ".join(
        [
            word.capitalize()
            for word in slugify(" ".join(episode.serial.title.split(" ")[:-1])).split(
            "-"
        )
        ]
    )
    if res is not None:
        new_name = f"{safe_words.replace(' ', '.')}.{s_number}{number}.{res}.{'.'.join(extra_infos)}.Cinemax.{ext}"
    else:
        new_name = f"{safe_words.replace(' ', '.')}.{s_number}{number}.{'.'.join(extra_infos)}.Cinemax.{ext}"
    print(f"new_name: {new_name}, filename: {file_name} extras: {extra_infos}")
    return new_name


def get_subtitle_path_episode(self, filename):
    return get_serial_root(
        self.episode.serial,
        f"episodes/season-{self.episode.season.number}/subs/subtitle-episode{self.episode.number}-{filename}",
    )


def get_subtitle_path_episode_vtt(self, filename):
    name = ".".join(str(filename).split(".")[:-1]) + ".vtt"
    return get_serial_root(
        self.episode.serial,
        f"season-{self.episode.season.number}/subs/subtitle-episode{self.episode.number}-{name}",
    )


class EpisodeSubtitle(models.Model):
    language = models.CharField(max_length=100, default="فارسی")
    srt = models.FileField(
        upload_to=get_subtitle_path_episode,
        validators=[FileExtensionValidator(allowed_extensions=["srt"])],
    )
    vtt = models.FileField(
        upload_to=get_subtitle_path_episode_vtt,
        validators=[FileExtensionValidator(allowed_extensions=["srt"])],
        null=True,
        blank=True,
    )
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    def __str__(self):
        return self.episode.serial.title + "-" + self.srt.name.split("/")[-1]


def get_subtitle_path_season(self, filename):
    return get_serial_root(
        self.season.serial, f"season-{self.season.number}/subtitle-{filename}"
    )


class SeasonSubtitle(models.Model):
    season = models.ForeignKey(Season, on_delete=models.DO_NOTHING)
    archive = models.FileField(
        upload_to=get_subtitle_path_season,
        validators=[FileExtensionValidator(allowed_extensions=["rar", "zip"])],
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.season.serial.title + "-" + self.archive.name.split("/")[-1]


def get_audio_path(self, filename):
    ext = filename.split(".")[-1]
    return get_serial_root(
        self.episode.serial,
        f"season-{self.episode.season.number}/audios/episode-{self.episode.number}-{self.language}-audio.{ext}",
    )


class Audio(models.Model):
    language = models.CharField(max_length=100)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=get_audio_path,
        validators=[FileExtensionValidator(allowed_extensions=["mp3", "aac"])],
    )

    def __str__(self):
        return f"{self.episode.serial.title}-episode {str(self.episode.number)[:20]}-{self.language}-audio"


def get_trailer_path(self, filename):
    return get_serial_root(
        self.serial,
        f"trailers/{filename}",
    )


class Trailer(models.Model):
    serial = models.ForeignKey(Serial, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    resolution = models.CharField(max_length=100, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to=get_trailer_path, validators=Video_Validator)

    def __str__(self):
        return f"{self.serial} {self.label}"
