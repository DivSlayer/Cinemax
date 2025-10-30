import json
import json
import mimetypes
import os
import re
from itertools import combinations
from wsgiref.util import FileWrapper

from django.http import HttpResponse, FileResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from Account.models import Account
from Error.models import Error
from Movie.models import Movie, Video, Subtitle
from Movie.values import get_movie_root
from Person.models import Person
from Rest.common_serializers import GetSourceSerializer
from Serial.models import Serial, Episode
from Tag.models import Tag
from Tool.check_soft import check_soft_sub
from Tool.get_soft_subtitle import SoftSubtitle
from Tool.views import convert_vtt, get_poster
from Utility.db_transfer import import_data
from Utility.imdb_handler import IMDBHandler
from Utility.no_serializer import get_object, all_serializer
from Utility.responses import list_response, single_response, error_response
from Utility.tools import adv_search_filter, ordering
from Category.models import Category
from Utility.views import get_duration, get_resolution, get_size


class GetSourceLink(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        uuid = request.GET.get('uuid', None)
        if uuid is not None:
            obj = get_object(uuid, use_imdb=False, use_slug=False)
            user = Account.objects.get(email=request.user.email)
            if type(obj) == Video:
                ins = GetSourceSerializer(obj, user)
                return Response(ins.serialize())
            elif type(obj) == Movie:
                data = []
                for video in Video.objects.filter(movie=obj):
                    ins = GetSourceSerializer(video, user)
                    data.append(ins.serialize())
                return Response(data)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def vitals(request):
    datas = {}
    min_year = Movie.objects.all().order_by("year").first().year
    datas["min_year"] = int(min_year)
    max_year = Movie.objects.all().order_by("-year").first().year
    datas["max_year"] = int(max_year)
    return HttpResponse(json.dumps(datas), content_type="application/json")


def main_list(request):
    all_together = []
    page = request.GET.get("page", 1)
    movies = Movie.objects.all()
    movies = adv_search_filter(request, movies)
    serials = Serial.objects.all()
    serials = adv_search_filter(request, serials)
    all_together.extend(movies)
    all_together.extend(serials)
    order = request.GET.get("order", None)
    ordered = ordering(all_together, order)
    serialized = []
    for obj in ordered:
        serialized.append(all_serializer(obj))
    return list_response(serialized, page=page, serialize=False)


def posters(request):
    all_together = []
    movies = [movie for movie in Movie.objects.filter(show_poster=True)]
    serials = [serial for serial in Serial.objects.all()]
    all_together.extend(movies)
    all_together.extend(serials)
    ordered = ordering(all_together, order="-published_at")
    return list_response(arr=ordered[:5], small=True)


def latest(request):
    all_together = []
    page = request.GET.get("page", 1)
    page = int(page)
    movies = [movie for movie in Movie.objects.filter(show_poster=True)]
    serials = [serial for serial in Serial.objects.all()]
    all_together.extend(movies)
    all_together.extend(serials)
    ordered = ordering(all_together, order="-published_at")
    return list_response(arr=ordered, small=True, page=page)


def single(request):
    imdb_id = request.GET.get("id", None)
    uuid = request.GET.get("uuid", None)
    slug = request.GET.get("slug", None)
    if imdb_id is not None:
        obj = get_object(imdb_id)
        serialized = all_serializer(obj)
        return single_response(serialized)
    if slug is not None:
        obj = get_object(slug, use_imdb=False, use_slug=True)
        serialized = all_serializer(obj)
        return single_response(serialized)
    if uuid is not None:
        obj = get_object(uuid, use_imdb=False, use_slug=False)
        serialized = all_serializer(obj)
        return single_response(serialized)
    return error_response()


def get_array(string):
    string = " ".join(slugify(string).split("-"))
    all_combinations = []
    for i in range(1, len(string)):
        coms = combinations(string.lower().split(" "), i)
        for com in coms:
            all_combinations.append(" ".join(com))
    return all_combinations


def search(request):
    found = []
    serialized = []
    search_val = request.GET.get("s", None)
    if search_val is not None:
        search_val = search_val.lower()
        for movie in Movie.objects.all():
            title_list = get_array(movie.title)
            if search_val in title_list:
                found.append(movie)
        for serial in Serial.objects.all():
            title_list = get_array(serial.title)
            if search_val in title_list:
                found.append(serial)
        for person in Person.objects.all():
            title_list = get_array(person.name)
            if search_val in title_list:
                found.append(person)
        for obj in found:
            serialized.append(all_serializer(obj))
        return list_response(
            serialized,
            serialize=False,
            per_page=len(serialized) if len(serialized) > 0 else 1,
        )
    return error_response()


def error(request):
    message = request.POST.get("message", "")
    error_ins = Error.objects.create(
        device=request.user_agent.os.family, message=message
    )
    error_ins.save()
    return HttpResponse("done")


def manual_update(request, slug):
    update = request.GET.get("update", False)
    get_image = request.GET.get("image", True)
    get_image = False if type(get_image) == str else True
    get_poster_c = request.GET.get("poster", True)
    get_poster_c = False if type(get_poster_c) == str else True
    proxy = request.GET.get("proxy", None)
    print(f"get poster c: {get_poster_c}")
    if proxy is not None:
        proxy = {
            "http": proxy if len(proxy.split(":")) > 1 else f"127.0.0.1:{proxy}",
            "https": proxy if len(proxy.split(":")) > 1 else f"127.0.0.1:{proxy}",
        }
    video = request.GET.get("video", False)

    obj = get_object(slug, use_imdb=False, use_slug=True)
    print(f"obj: {obj}")
    result = []
    if update:
        movie_handled, got_poster = IMDBHandler(
            obj, proxy, get_image=get_image, get_poster=get_poster_c
        ).start()
        result = [
            {
                "title": "لینک",
                "value": f"<a class='text-primary' href=/movie/{movie_handled.slug}> مشاهده </a>",
                "color": "green",
            },
            {
                "title": "دریافت پوستر",
                "value": "انجام شد" if got_poster else "انجام نشد!",
                "color": "green" if got_poster else "red",
            },
        ]
        return HttpResponse(
            json.dumps(result), content_type="application/json", status=200
        )
    if video:
        video_name = get_movie_root(obj, video, use_media=False)
        video_instance = Video.objects.create(movie=obj)
        video_instance.file.name = video_name
        video_instance.save()
        video_instance.repair_name()
        video_instance.add_tag()
        check_soft_sub(video_instance.file.name, video_instance.uuid)
        movie_res = int(obj.resolution.replace("p", "")) if obj.resolution else None
        video_res = (
            int(video_instance.resolution.replace("p", ""))
            if video_instance.resolution
            else None
        )
        obj.duration = video_instance.duration
        obj.save()
        if video_res is not None:
            if movie_res is not None:
                if video_res > movie_res:
                    obj.resolution = video_instance.resolution
                    obj.save()
            else:
                obj.resolution = video_instance.resolution
                obj.save()
        return HttpResponse(
            json.dumps(
                {
                    "resolution": video_instance.resolution,
                    "duration": video_instance.duration,
                }
            ),
            content_type="application/json",
        )
    if get_poster_c and update == False:
        poster_res = get_poster(obj, proxy=proxy)
        if poster_res is not None:
            poster_img = poster_res.replace("media/", "")
            obj.poster_img.name = poster_img
            obj.save()
    return HttpResponse(json.dumps(result), content_type="application/json")


def fix(request):
    data = []
    videos = Video.objects.filter(subbed=False)[5:10]
    data.append([video.file.name for video in videos])
    return JsonResponse({'videos':data})


def get_sub_nums(video_path, root_folder):
    sub_nums = 0
    metadata_path = root_folder + "/metadata.json"
    print(metadata_path)
    meta_data_command = f'ffprobe -loglevel 0 -print_format json -show_format -show_streams "{video_path}" > "{metadata_path}"'
    value = os.system(meta_data_command)
    if value == 0:
        content = ""
        with open(metadata_path, "r", encoding="utf8") as f:
            content = json.loads(f.read())
        if content["streams"]:
            for stream in content["streams"]:
                if stream["codec_type"] and stream["codec_type"] == "subtitle":
                    sub_nums += 1
        return sub_nums
    else:
        return 0


def get_forbidden(request):
    tag = Tag.objects.get(en_title='forbidden')
    movies = Movie.objects.filter(tags__en_title__in=[tag.en_title])
    return render(request, 'forbidden.html', context={
        'forbiddens': movies
    })


def get_all(request):
    movies = Movie.objects.all()
    return render(request, 'forbidden.html', context={
        'forbiddens': movies
    })


# movies/fantastic mr fox 2009-R7eWATa33W/Fantastic.MrFox.2009.1080p.Cinemax.mkv
# movies/fantastic mr. fox 2009-R7eWATa33W/Fantastic.MrFox.2009.1080p.Cinemax.mkv


class StreamVideo(APIView):
    permissions = (permissions.IsAuthenticated,)

    def get(self, request, uuid):
        """Correct video streaming implementation with proper FileResponse usage"""
        obj = get_object(uuid, use_imdb=False)

        file_path = obj.file.path if type(obj) == Video else obj.video.path
        print(file_path)
        if not os.path.exists(file_path):
            return Response({'error': "Video file not found"}, status=status.HTTP_404_NOT_FOUND)

        file_size = os.path.getsize(file_path)
        range_header = request.headers.get('Range', '').strip()

        # Open the file once and reuse the file object
        file = open(file_path, 'rb')

        # Handle full file request
        if not range_header:
            response = FileResponse(file)
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
            response['Content-Length'] = file_size
            response['Accept-Ranges'] = 'bytes'
            return response

        # Handle range requests
        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if not match:
            file.close()
            return Response({'error': "Invalid range header"}, status=status.HTTP_400_BAD_REQUEST)

        first_byte = int(match.group(1))
        last_byte = int(match.group(2)) if match.group(2) else file_size - 1

        if first_byte >= file_size:
            file.close()
            return Response({"error": "Invalid range start"}, status=status.HTTP_400_BAD_REQUEST)

        last_byte = min(last_byte, file_size - 1)
        content_length = last_byte - first_byte + 1

        # Create the response with proper headers
        response = FileResponse(
            file,
            status=206,
            content_type='video/mp4'
        )
        response['Content-Length'] = content_length
        response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{file_size}'
        response['Accept-Ranges'] = 'bytes'
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'

        # Seek to the correct position
        file.seek(first_byte)

        # Set up streaming content
        response.streaming_content = (
            file.read(chunk_size) for chunk_size in [8192] * (content_length // 8192) + [content_length % 8192]
        )

        return response


class DownloadVideo(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request, uuid):
        """Handle downloads for allowed plans"""
        # TODO: Hanle Authentication
        # if not request.user.is_authenticated:
        #     return HttpResponseForbidden("Authentication required")
        obj = get_object(uuid, use_imdb=False)
        # print(request.user)
        # account = Account.objects.get(email=request.user.email)
        # if not account.plan.download_available:
        #     return HttpResponseForbidden("Downloads not allowed for your plan")

        file_path = obj.file.path
        file_wrapper = FileWrapper(open(file_path, 'rb'))
        content_type = mimetypes.guess_type(file_path)[0]
        response = HttpResponse(file_wrapper, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        response['Content-Length'] = os.path.getsize(file_path)
        return response
