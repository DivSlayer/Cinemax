import os

from django.shortcuts import render
import json
from django.http import HttpResponse
from Movie.forms import CreateMovie
from Serial.forms import CreateEpisode, CreateSerial
from Serial.models import Episode, Serial
from Tool.check_soft import check_soft_sub
from Tool.views import convert_vtt
from Movie.models import Subtitle as MovieSubtitle, Movie, Video
from Utility.imdb_handler import IMDBHandler
from Utility.views import get_duration, get_resolution, get_size


def episode(request):
    if request.FILES.get('videos[]', None) is not None:
        videos = request.FILES.getlist('videos[]')
        current = request.POST.get('number')
        form = CreateEpisode(request.POST)
        current = int(current)
        valid = form.is_valid()
        for video in videos:
            e_series = form.cleaned_data['serial']
            e_season = form.cleaned_data['season']
            find = Episode.objects.filter(season=e_season, serial=e_series, number=current)
            if len(find) > 0:
                find.first().delete()
            episode_ins = Episode(video=video,
                                  number=current,
                                  season=e_season,
                                  serial=e_series)
            episode_ins.save()
            episode_ins.resolution = get_resolution(episode_ins.video.path)
            episode_ins.size = get_size(episode_ins.video.path)
            episode_ins.duration = get_duration(episode_ins.video.path)
            episode_ins.save()
            print(f"{video}")
            episode_ins.repair_name(f"{video}")
            episode_ins.add_tag()
            check_soft_sub(f"{video}", episode_ins.uuid)
            if not e_series.resolution:
                e_series.resolution = episode_ins.resolution
                e_series.save()
            e_series.duration = int(episode_ins.duration) + int(
                e_series.duration) if e_series.duration else episode_ins.duration
            e_series.save()
            current += 1
        return HttpResponse(json.dumps({'result': 'Uploaded Successfully!'}),
                            content_type='application/json',
                            status=200)
    else:
        return HttpResponse(json.dumps({'result': 'bad request'}),
                            content_type='application/json',
                            status=400)


def handle_movie_video(request, movie: Movie):
    video = request.FILES.get('video', None)
    if video is not None:
        video_instance = Video.objects.create(movie=movie, file=video)
        video_instance.save()
        video_instance.repair_name()
        check_soft_sub(f"{video}", video_instance.uuid)
        movie_res = int(movie.resolution.replace('p', '')) if movie.resolution else None
        video_res = int(video_instance.resolution.replace('p', '')) if video_instance.resolution else None
        movie.duration = video_instance.duration
        movie.save()
        if video_res is not None:
            if movie_res is not None:
                if video_res > movie_res:
                    movie.resolution = video_instance.resolution
                    movie.save()
            else:
                movie.resolution = video_instance.resolution
                movie.save()


def movie(request):
    if request.method == 'POST':
        form = CreateMovie(request.POST)
        proxy = request.POST.get('proxy', None)
        if proxy is not None:
            proxy = {
                'http': proxy if len(proxy.split(':')) > 1 else f"127.0.0.1:{proxy}",
                'https': proxy if len(proxy.split(':')) > 1 else f"127.0.0.1:{proxy}",
            }
        if form.is_valid():
            franchise = form.cleaned_data['franchise']
            imdb_id = form.cleaned_data['imdb_id']
            title = form.cleaned_data['title']
            movie_instance = Movie.objects.create(imdb_id=imdb_id, title=title, franchise=franchise)
            movie_instance.save()
            returned = IMDBHandler(movie_instance, proxy, get_image=True).start()
            movie_handled, got_poster = returned
            handle_movie_video(request, movie_handled)
            result = [{
                "title": "لینک",
                "value": f"<a class='text-primary' href=/movie/{movie_handled.slug}> مشاهده </a>",
                "color": "green",
            }, {
                "title": "دریافت پوستر",
                "value": "انجام شد" if got_poster else "انجام نشد!",
                "color": "green" if got_poster else 'red',
            }]
            return HttpResponse(json.dumps(result),
                                content_type='application/json',
                                status=200)
    else:
        return HttpResponse(json.dumps({'result': 'Something went wrong!'}),
                            content_type='application/json',
                            status=400)


def serial(request):
    if request.method == 'POST':
        form = CreateSerial(request.POST)
        proxy = request.POST.get('proxy', None)
        if proxy is not None:
            proxy = {
                'http': proxy if len(proxy.split(':')) > 1 else f"127.0.0.1:{proxy}",
                'https': proxy if len(proxy.split(':')) > 1 else f"127.0.0.1:{proxy}",
            }
        if form.is_valid():
            imdb_id = form.cleaned_data['imdb_id']
            title = form.cleaned_data['title']
            movie_instance = Serial.objects.create(imdb_id=imdb_id, title=title)
            movie_instance.save()
            returned = IMDBHandler(movie_instance, proxy, get_image=True).start()
            movie_handled, got_poster = returned
            result = [{
                "title": "لینک",
                "value": f"<a class='text-primary' href=/movie/{movie_handled.slug}> مشاهده </a>",
                "color": "green",
            }, {
                "title": "دریافت پوستر",
                "value": "انجام شد" if got_poster else "انجام نشد!",
                "color": "green" if got_poster else 'red',
            }]
            return HttpResponse(json.dumps(result),
                                content_type='application/json',
                                status=200)
    else:
        return HttpResponse(json.dumps({'result': 'Something went wrong!'}),
                            content_type='application/json',
                            status=400)
