import json
import os.path
import shutil

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
# from Movie.forms import CreateMovieSubtitle
from Movie.models import Movie, Subtitle as MovieSubtitle, Franchise, Video
from Movie.values import get_movie_root
from Rest.common_serializers import SmallMovieSerializer
from Serial.models import EpisodeSubtitle, Serial, Season, Episode
from Serial.values import get_episode_path
from Tool.audio_handler import AudioHandler
from Tool.get_soft_subtitle import SoftSubtitle
from Tool.views import convert_vtt
from Utility.no_serializer import get_object
from Utility.responses import paginator


# Create your views here.
# def index(request):
#     return render(request, 'Dashboard/index.html', {'current': 'home-home'})
def index(request, *args, **kwargs):
    return render(request, 'dashboard/v2/index.html', {'current': 'home-home'})




def movie(request):
    context = {
        'current': 'uploads-movie',
        'franchise': Franchise.objects.all(),
        'url': '/upload/movie',
    }
    return render(request, 'dashboard/upload-movie.html', context)


def franchise(request):
    context = {
        'current': 'uploads-serial',
        'url': '/upload/franchise',
    }
    return render(request, 'dashboard/upload-franchise.html', context)


def serial(request):
    context = {
        'current': 'uploads-serial',
        'url': '/upload/serial',
    }
    return render(request, 'dashboard/upload-serial.html', context)


def season(request):
    return render(
        request, 'dashboard/season.html', {
            'current': 'uploads-season',
            'serials': Serial.objects.all(),
            'url': '/upload/season'
        })


def episode(request):
    serials = Serial.objects.all()
    seasons = Season.objects.all()
    return render(
        request, 'dashboard/episode.html', {
            'current': 'uploads-episode',
            'url': '/upload/episode',
            'serials': serials,
            'seasons': seasons
        })


def movie_sub(request):
    if request.method == 'POST':
        form = CreateMovieSubtitle(request.POST)
        form.is_valid()
        movie_cleaned = form.cleaned_data['movie']
        result = handle_movie_subs(request, movie_cleaned)
        print(f'result: {result}')
        if result:
            return HttpResponse(json.dumps(
                {'result': 'Uploaded Successfully!'}),
                content_type='application/json')
        else:
            return error_went_wrong()
    if request.method == 'GET':
        movies = Movie.objects.all()
        context = {
            'current': 'uploads-movies-sub',
            'url': '/dashboard/upload-movie-subtitle',
            'movies': movies,
        }
        return render(request, 'dashboard/movie-sub.html', context)


def season_sub(request):
    return None


def episode_sub(request):
    return None


def data_movies(request):
    movies_page, movies_range = paginator(Video.objects.all().order_by('-published_at'), 1, 700)
    context = {
        'count': len(Movie.objects.all()),
        'page': movies_page,
        'page_range': movies_range,
        'current': 'datas-movies'
    }
    return render(request, 'dashboard/data-movies.html', context)


def data_serial(request):
    movies_page, movies_range = paginator(Movie.objects.all())
    context = {
        'movies_count': len(Movie.objects.all()),
        'movies_page': movies_page,
        'movies_range': movies_range,
        'current': 'datas-movies'
    }
    return render(request, 'dashboard/data-movies.html', context)


def data_seasons(request):
    page, p_range = paginator(Season.objects.all())
    context = {
        'count': len(Season.objects.all()),
        'page': page,
        'page_range': p_range,
        'current': 'datas-seasons'
    }
    return render(request, 'dashboard/data-seasons.html', context)


def data_movies_sub(request):
    page, p_range = paginator(MovieSubtitle.objects.all())
    context = {
        'count': len(MovieSubtitle.objects.all()),
        'page': page,
        'page_range': p_range,
        'current': 'datas-movies-sub'
    }
    return render(request, 'dashboard/data-movies-sub.html', context)


def data_episodes(request):
    if request.method == 'POST':
        print(request.POST)
    page, p_range = paginator(Episode.objects.all(),
                              per_page=len(Episode.objects.all()))
    context = {
        'count': len(Episode.objects.all()),
        'page': page,
        'page_range': p_range,
        'current': 'datas-episodes'
    }
    return render(request, 'dashboard/data-episodes.html', context)


def data_episodes_sub(request):
    page, p_range = paginator(EpisodeSubtitle.objects.all())
    context = {
        'count': len(EpisodeSubtitle.objects.all()),
        'page': page,
        'page_range': p_range,
        'current': 'datas-episodes-sub'
    }
    return render(request, 'dashboard/data-episodes-sub.html', context)


def remove_datas(request):
    if request.method == "POST":
        uuids = request.POST.get('uuids', None)
        print(uuids)


def delete_object(request):
    if request.method == "POST":
        uuids = request.POST.get('selections', None)
        if uuids is not None:
            uuids = uuids.split(',')
            for uuid in uuids:
                instance = get_object(uuid)
                if instance is not None:
                    folder_path = "./media/" + '/'.join(instance.detail_img.name.split('/')[0:-1])
                    print(folder_path)
                    print(instance.detail_img.name.split('/')[0:-1])
                    shutil.rmtree(folder_path)
                    instance.delete()
            return HttpResponse(json.dumps(
                {'result': 'Episodes deleted successfully'}),
                content_type='application/json')
        return error_went_wrong()
    return error_went_wrong()


def get_soft(request):
    if request.method == "POST":
        uuids = request.POST.get('selections', None)
        if uuids is not None:
            datas = []
            uuids = uuids.split(',')
            subtitles = SoftSubtitle(uuids).action()
            for subtitle in subtitles:
                if type(subtitle) == MovieSubtitle:
                    new_form = {
                        'title': subtitle.movie.title,
                        'url': subtitle.srt.url,
                        'result': 'انجام شد',
                        'color': 'green',
                    }
                    datas.append(new_form)
                if type(subtitle) == EpisodeSubtitle:
                    new_form = {
                        'title': f'{subtitle.episode}',
                        'url': subtitle.srt.url,
                        'result': 'انجام شد',
                        'color': 'green',
                    }
                    datas.append(new_form)
            return HttpResponse(json.dumps({'datas': datas}),
                                content_type='application/json')
        else:
            return error_went_wrong()


def check_status(request):
    if request.method == "POST":
        uuids = request.POST.get('selections', None)
        if uuids is not None:
            datas = []
            uuids = uuids.split(',')
            for uuid in uuids:
                instance = get_object(uuid)
                if type(instance) == Episode:
                    check, error = episode_check(instance)
                    new_form = {
                        'title':
                            f'episode{instance.number}-season{instance.season.number}-{instance.serial.title}',
                        'url': f'/s/{instance.serial.uuid}',
                        'result': 'عالی' if check else error,
                        'color': 'green' if check else 'red',
                    }
                    datas.append(new_form)
                if type(instance) == Movie:
                    check = movie_check(instance)
                    new_form = {
                        'title': f'{instance.title}',
                        'url': f'/m/single/{instance.uuid}',
                        'result': 'عالی' if check else 'مشکل',
                        'color': 'green' if check else 'red',
                    }
                    datas.append(new_form)
            return HttpResponse(json.dumps({'datas': datas}),
                                content_type='application/json')
        else:
            return error_went_wrong()
    else:
        return error_went_wrong()


def episode_check(instance):
    video_check = os.path.isfile(instance.video.path)
    number_check = instance.number
    serial_check = instance.serial.title
    season_check = instance.season.number
    errors = []
    result = True
    if not video_check:
        result = False
        errors.append('فایل ویدیویی وجود ندارد')
    if number_check is None:
        result = False
        errors.append('شماره قسمت اشتباه است')
    if serial_check is None:
        result = False
        errors.append('نام سریال اشتباه است')
    if season_check is None:
        result = False
        errors.append('فصل وجود ندارد')
    if '/'.join(instance.video.name.split('/')
                [:-1]).lower() != get_episode_path(instance):
        result = False
        errors.append('مسیر فایل ویدیویی اشتباه است')
        print('/'.join(instance.video.name.split('/')[:-1]).lower())
        print(get_episode_path(instance))
    return result, ', '.join(errors)


def movie_check(instance):
    video_check = os.path.isfile(instance.video.path)
    bg_img_check = os.path.isfile(instance.bg_image.path)
    detail_img_check = os.path.isfile(instance.detail_img.path)
    title_check = instance.title
    result = True
    if not video_check:
        result = False
    if title_check is None:
        result = False
    if not bg_img_check:
        result = False
    if not detail_img_check:
        result = False
    if '/'.join(instance.video.path.split('/')) != get_movie_root(instance):
        result = False
    if '/'.join(instance.video.path.split('/')) != get_movie_root(instance):
        result = False
    if '/'.join(instance.video.path.split('/')) != get_movie_root(instance):
        result = False
    return result


def error_went_wrong():
    return HttpResponse(json.dumps({'result': 'Something went wrong!'}),
                        content_type='application/json',
                        status=400)


def get_audios(request):
    if request.method == "POST":
        uuids = request.POST.get('selections', None)
        if uuids is not None:
            datas = []
            uuids = uuids.split(',')
            for uuid in uuids:
                obj = get_object(uuid, use_imdb=False)
                if obj is not None:
                    try:
                        audios_path = AudioHandler(obj).action()
                        new_form = {
                            'title': obj.title if type(
                                obj) == Movie else f'episode{obj.number}-season{obj.season.number}-{obj.serial.title}',
                            'url': f'/movie/{obj.slug}' if type(obj) == Movie else f'/serial/{obj.serial.slug}',
                            'result': ", ".join(["/".join(audio.split('/')[-2:]) for audio in audios_path]),
                            'color': 'green',
                        }
                        datas.append(new_form)
                    except Exception as e:
                        print(e)
                        title = ""
                        if type(obj) == Movie:
                            title = obj.title
                        if type(obj) == Episode:
                            title = f'episode{obj.number}-season{obj.season.number}-{obj.serial.title}',
                        new_form = {
                            'title': title,
                            'url': f'{obj.uuid}',
                            'result': "خطا",
                            'color': 'red',
                        }
                        datas.append(new_form)
            return HttpResponse(json.dumps({'datas': datas}),
                                content_type='application/json')
        else:
            return error_went_wrong()

    else:
        return error_went_wrong()


def handle_movie_subs(request, movie_instance):
    if request.FILES.get('subs[]', None) is not None:
        subtitles = []
        for sub in request.FILES.getlist('subs[]'):
            subtitle_instance = MovieSubtitle(srt=sub, movie=movie_instance)
            subtitle_instance.save()
            if convert_vtt(subtitle_instance.srt.path):
                subtitle_instance.vtt.name = subtitle_instance.srt.name.replace('.srt', '') + '.vtt'
                subtitle_instance.save()
            else:
                os.remove(subtitle_instance.srt.path)
                subtitle_instance.delete()
        return True
    else:
        return False
