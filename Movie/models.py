from itertools import combinations
import json
import os
import shutil
from datetime import datetime
from random import randint
import re

import webvtt
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from Category.models import Category
from Country.models import Country
from Movie.values import get_movie_root
from Person.models import Person
from Tag.models import Tag
from Utility.views import (
    get_uuid,
    Image_Validator,
    Video_Validator,
    get_resolution,
    get_size,
    get_duration, get_sub_audio_nums,
)
from video_encoding.fields import VideoField


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
        input_string = " ".join([word.capitalize()
                                for word in input_string.split(" ")])
    return input_string


def get_poster_path(movie, filename):
    return get_movie_root(movie, "poster.jpg")


def get_item_path(movie, filename):
    return get_movie_root(movie, "item_img.jpg")


def get_compress_path(movie, filename):
    return get_movie_root(movie, "compress_img.jpg")


class Franchise(models.Model):
    name = models.CharField(max_length=100)
    uuid = models.CharField(max_length=10, default=get_uuid, unique=True)
    published_at = models.DateTimeField(
        auto_now=False, auto_now_add=True, null=True, blank=True
    )

    class Meta:
        verbose_name = "Franchise"
        verbose_name_plural = "     Franchises"
        ordering = ("-published_at",)

    def __str__(self):
        return self.name


class Movie(models.Model):
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
    en_story = models.TextField(blank=True, null=True)
    fa_story = models.TextField(blank=True, null=True)
    franchise = models.ForeignKey(
        Franchise, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    cast = models.ManyToManyField(
        Person, blank=True, related_name="movie_cast")
    writers = models.ManyToManyField(
        Person, blank=True, related_name="movie_writers")
    directors = models.ManyToManyField(
        Person, blank=True, related_name="movie_directors"
    )
    show_poster = models.BooleanField(default=True)
    ultra = models.BooleanField(default=False)
    published_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    qrCode = models.TextField(null=True, blank=True)
    second_color = models.TextField(null=True, blank=True)
    third_color = models.TextField(null=True, blank=True)
    freq_color = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=1000, null=True, blank=True)
    release_date = models.DateField(
        null=True, blank=True, auto_now_add=False, auto_now=False
    )
    subbed = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name="movie_tags", blank=True)

    def __str__(self):
        return self.title + "-" + self.uuid

    class Meta:
        ordering = ("-published_at",)
        verbose_name_plural = "    Movies"

    def get_posters(self):
        randoms = []
        randoms_obj = []
        movies = Movie.objects.filter(show_poster=True)
        while len(randoms_obj) <= 10:
            random_num = randint(0, len(movies) - 1)
            if random_num not in randoms:
                randoms.append(random_num)
                randoms_obj.append(movies[random_num])
        return randoms_obj


@receiver(pre_save, sender=Movie)
def my_callback(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.title)
    instance.url = f"/movie/{slugify(instance.title)}"


def get_video_file_path(self, filename):
    return get_movie_root(self.movie, filename)


class Video(models.Model):

    STATUS_CHOICES = [
        ('nothing', 'Nothing'),
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]

    ACTION_CHOICES = [
        ('subtitle', 'Subtitle'),
        ('intro', 'Intro'),
    ]

    uuid = models.CharField(max_length=10, default=get_uuid)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    file = VideoField(
        upload_to=get_video_file_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["MOV", "avi", "mp4", "webm", "mkv"]
            )
        ],
    )
    resolution = models.CharField(max_length=300, null=True, blank=True)
    duration = models.CharField(max_length=300, null=True, blank=True)
    size = models.CharField(max_length=300, null=True, blank=True)
    sizeb = models.CharField(max_length=300, null=True, blank=True)
    published_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    subbed = models.BooleanField(default=False)
    dubbed = models.BooleanField(default=False)
    has_intro = models.BooleanField(default=False)
    censors = models.TextField(blank=True, null=True, default="[]")
    credits = models.TextField(blank=True, null=True, default="[]")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="nothing")
    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, blank=True, null=True)
    json_data = models.JSONField(null=True, blank=True, default=dict)
    error_message = models.TextField(blank=True,null=True)
    last_update = models.DateTimeField(auto_now=True,auto_now_add=False)
    
    def __str__(self):
        return f"{self.movie.title} {self.resolution}-{self.uuid}"

    class Meta:
        verbose_name_plural = "   Videos"

    def repair_name(self):
        if os.path.isfile(self.file.path):
            res = get_resolution(self.file.path)
            size = get_size(self.file.path)
            sizeb = get_size(self.file.path, bytes=True)
            duration = get_duration(self.file.path)
            self.resolution = res
            self.size = size
            self.sizeb = sizeb
            self.duration = duration
            old_name = self.file.name
            old_path = f"media/{old_name}"
            new_name = get_video_name(self, old_name.split("/")[-1], res)
            new_path = get_movie_root(self.movie, new_name, use_media=True)
            if old_path != new_path:
                shutil.move(old_path, new_path)
            self.file.name = get_movie_root(self.movie, new_name)
            self.save()
            return f"{self} Done!"
        return f"{self} error!"

    def add_tag(self):
        if os.path.isfile(self.file.path):
            ext = self.file.name.split(".")[-1]
            output_vid = f'media/{"/".join(self.file.name.split("/")[:-1])}/tagged.mkv'
            output_vid = os.path.join(os.getcwd(), output_vid)
            with open(output_vid, "w") as f:
                pass
            sub_num, audio_num = get_sub_audio_nums(
                self.file.path,
                root_folder=f'media/{"/".join(self.file.name.split("/")[:-1])}',
            )
            sub_string = ""
            audio_string = ""
            for i in range(0, sub_num):
                sub_string += f' -metadata:s:s:{i} title="Persian - Cinemax.com" -metadata:s:s:{i} language="Persian"'
            for i in range(0, audio_num):
                audio_string += f' -metadata:s:a:{i} title="Persian - Cinemax.com" -metadata:s:a:{i} language="Persian"'
            command = f'ffmpeg -i "{self.file.path}" -metadata title="{self.movie.title} {self.resolution} - Cinemax.com" -codec copy -c:v copy -c:a copy -c:s copy  -metadata:s:v:0 title="Cinemax.com"  -metadata:s:v:0 handler="Cinemax.com" -metadata:s:v:0 comment="Cinemax.com" {sub_string} {audio_string} -y "{output_vid}"'
            value = os.system(command)
            if value == 0 and os.path.isfile(output_vid):
                path = self.file.path
                os.remove(self.file.path)
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


def get_video_name(video, old_name, res=None):
    file_name = ".".join(old_name.split(".")[:-1])
    ext = old_name.split(".")[-1]
    combs = get_array(video.movie.title)
    combs.extend(slugify(video.movie.title).split("-"))
    sites = settings.env.list("IMPORT_SITES", default=[])
    reses = ["2160p", "1080p", "720p", "480p", "360p", "240p"]
    extra_infos = []
    extras = file_name.split(".")
    if not len(extras) > 1:
        extras = file_name.split("_")
    for word in extras:
        if (
                word.lower() not in combs
                and word.lower() not in reses
                and word.lower() != "cinemax"
                and word.lower() not in sites
        ):
            extra_infos.append(word)
    safe_words = " ".join(
        [word.capitalize() for word in slugify(video.movie.title).split("-")]
    )
    if res is not None:
        new_name = f"{safe_words.replace(' ', '.')}.{res}.{'.'.join(extra_infos)}.Cinemax.{ext}"
    else:
        new_name = (
            f"{safe_words.replace(' ', '.')}.{'.'.join(extra_infos)}.Cinemax.{ext}"
        )
    print(new_name)
    return new_name


def get_subtitle_path(self, filename):
    index = len(Subtitle.objects.filter(video=self.video))
    return get_movie_root(self.video.movie, f"subs/subtitle-{self.video.uuid}-{index}.srt")


def get_subtitle_path_vtt(self, filename):
    name = ".".join(str(filename).split(".")[:-1]) + ".vtt"
    return get_movie_root(self.video.movie, f"subs/subtitle-{self.video.uuid}-{name}")


class Subtitle(models.Model):
    uuid = models.CharField(max_length=10, default=get_uuid)
    language = models.CharField(max_length=100, default="فارسی")
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    srt = models.FileField(
        upload_to=get_subtitle_path,
        validators=[FileExtensionValidator(allowed_extensions=["srt"])],
    )
    vtt = models.FileField(
        upload_to=get_subtitle_path_vtt,
        validators=[FileExtensionValidator(allowed_extensions=["vtt"])],
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.video.movie.title + " " + self.video.resolution + "-" + self.srt.name.split("/")[-1]

    class Meta:
        verbose_name_plural = "  Subtitles"


@receiver(post_delete, sender=Subtitle)
def subtitle_post_delete(sender, instance, using, **kwargs):
    if instance.srt and os.path.isfile(instance.srt.path):
        os.remove(instance.srt.path)
    if instance.vtt and os.path.isfile(instance.vtt.path):
        os.remove(instance.vtt.path)


@receiver(post_save, sender=Subtitle)
def subtitle_post_save(sender, instance, using, **kwargs):
    # Time to convert vtt
    print('Im the after save')
    if os.path.isfile(instance.srt.path) and not instance.vtt:
        vtt = convert_vtt(instance.srt.path)
        if vtt is True:
            instance.vtt.name = instance.srt.name.replace('.srt', '') + '.vtt'
            instance.save()


def convert_vtt(path):
    try:
        webvtt.from_srt(path).save(path.replace('.srt', '') + '.vtt')
        return True
    except Exception as e:
        print(e)
        return False


def get_audio_path(self, filename):
    ext = filename.split(".")[-1]
    return get_movie_root(self.movie, f"audios/{self.language}-audio.{ext}")


class Audio(models.Model):
    language = models.CharField(max_length=100)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=get_audio_path,
        validators=[FileExtensionValidator(
            allowed_extensions=["mp3", "aac", "mka"])],
    )

    def __str__(self):
        return f"{str(self.movie.title)[:20]}-{self.language}-audio"

    class Meta:
        verbose_name_plural = " Audios"


def get_trailer_path(self, filename):
    return get_movie_root(
        self.movie,
        f"trailers/{filename}",
    )


class Trailer(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    resolution = models.CharField(max_length=100, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to=get_trailer_path,
                            validators=Video_Validator)

    def __str__(self):
        return f"{self.movie} {self.label}"
