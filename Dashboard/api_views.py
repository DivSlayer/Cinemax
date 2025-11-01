import json
import os

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from Account.models import Account
from Dashboard.views import error_went_wrong
from Movie.models import Movie, Video, Subtitle as MovieSubtitle, Subtitle
from Rest.common_serializers import SmallMovieSerializer, SubtitleSerializer
from Serial.forms import CreateEpisodeSub
from Serial.models import Episode, EpisodeSubtitle, Season
from Tool.softsub_handler import SoftSubtitle
from Tool.views import convert_vtt
from Utility.no_serializer import get_object
from Movie.forms import CreateMovieSubtitle


class HomePage(APIView):
    def get(self, request):
        movies = Movie.objects.all().order_by('-release_date')[:10]
        serializer = SmallMovieSerializer(movies, many=True).data
        return Response({'movies': serializer})


def check_videos(request, uuid):
    obj = get_object(uuid, use_imdb=False, use_slug=False)
    datas = []
    if type(obj) == Movie:
        videos = Video.objects.filter(movie=obj)
        print(f"There are: {len(videos)}")
        for video in videos:
            new_form = {
                "title": video.resolution
                if video.resolution
                else f"no resolution {video.size}",
                "result": os.path.isfile(video.file.path),
            }
            datas.append(new_form)

    if type(obj) == Season:
        videos = Episode.objects.filter(season=obj)
        for video in videos:
            new_form = {
                "title": video.resolution
                if video.resolution
                else f"no resolution {video.size}",
                "result": os.path.isfile(video.file.path),
            }
            datas.append(new_form)
    return HttpResponse(json.dumps(datas), content_type="application/json")


def check_subs(request, uuid):
    obj = get_object(uuid, use_imdb=False, use_slug=False)
    datas = []
    if type(obj) == Movie:
        videos = Video.objects.filter(movie=obj)
        for video in videos:
            subs = Subtitle.objects.filter(video=video)
            for sub in subs:
                srt_form = {
                    "title": sub.srt.name.split('/')[-1] + " for " + video.resolution,
                    "result": os.path.isfile(sub.srt.path),
                }
                vtt_form = {
                    "title": sub.vtt.name.split('/')[-1] + " for " + video.resolution,
                    "result": os.path.isfile(sub.vtt.path),
                }
                datas.append(srt_form)
                datas.append(vtt_form)
    if type(obj) == Season:
        videos = Episode.objects.filter(season=obj)
        for video in videos:
            new_form = {
                "title": video.resolution
                if video.resolution
                else f"no resolution {video.size}",
                "value": "سالم" if os.path.isfile(video.video.path) else "خطا",
                "done": os.path.isfile(video.video.path),
            }
            datas.append(new_form)
    return HttpResponse(json.dumps(datas), content_type="application/json")


def check_images(request, uuid):
    obj = get_object(uuid, use_imdb=False, use_slug=False)
    datas = []
    images = [
        {
            "title": "Poster Image",
            "path": obj.poster_img.path if obj.poster_img else None,
        },
        {
            "title": "Item Image",
            "path": obj.item_img.path if obj.item_img else None,
        },
        {
            "title": "Compressed Image",
            "path": obj.compress_img.path if obj.compress_img else None,
        },
    ]
    for image in images:
        new_form = {
            "title": image["title"],
            "result": image["path"] is not None and os.path.isfile(image["path"]),
        }
        datas.append(new_form)

    return HttpResponse(json.dumps(datas), content_type="application/json")


def censor(request, uuid):
    obj = get_object(uuid, use_imdb=False, use_slug=False)
    if type(obj) == Video:
        title = obj.movie.title + " " + obj.resolution
    else:
        title = obj.serial.title + " " + obj.resolution
    obj.censors = request.POST.get("cen", [])
    obj.save()
    new_form = {"title": title, "censors": json.loads(request.POST.get("cen", None))}
    return HttpResponse(json.dumps(new_form), content_type="application/json")


def credits(request, uuid):
    obj = get_object(uuid, use_imdb=False, use_slug=False)
    if type(obj) == Video:
        title = obj.movie.title + " " + obj.resolution
    else:
        title = obj.serial.title + " " + obj.resolution
    obj.credits = request.POST.get("creds", [])
    obj.save()
    new_form = {"title": title, "credits": json.loads(request.POST.get("creds", None))}
    return HttpResponse(json.dumps(new_form), content_type="application/json")


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])  # <-- Set your permission class here
def add_soft(request, uuid):
    try:
        video = Video.objects.get(uuid=uuid)
        form = CreateMovieSubtitle(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.video = video
            instance.save()
            video.action = 'subtitle'
            video.status = 'queued'
            video.save()
            return Response({})
        else:
            return Response({'error': form.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


def handle_movie_subs(request, movie_instance):
    if request.FILES.get("subs[]", None) is not None:
        subtitles = []
        for sub in request.FILES.getlist("subs[]"):
            print(type(movie_instance))
            if type(movie_instance) == Episode:
                subtitle_instance = EpisodeSubtitle(srt=sub, episode=movie_instance)
            elif type(movie_instance) == Video:
                subtitle_instance = MovieSubtitle(srt=sub, movie=movie_instance.movie)
            subtitle_instance.save()
            if convert_vtt(subtitle_instance.srt.path):
                subtitle_instance.vtt.name = (
                        subtitle_instance.srt.name.replace(".srt", "") + ".vtt"
                )
                subtitle_instance.save()
                subtitles.append(subtitle_instance)
            else:
                print("not converted")
                os.remove(subtitle_instance.srt.path)
                subtitle_instance.delete()
        return subtitles
    else:
        return False


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])  # <-- Set your permission class here
def cancel_action(request, uuid):
    video = Video.objects.get(uuid=uuid)
    video.status = "CANCELED"
    video.save()
    return Response()


@api_view(['GET'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])  # <-- Set your permission class here
def add_intro(request, uuids):
    print(uuids)
    uuids = uuids.split(',')
    for uuid in uuids:
        video = Video.objects.get(uuid=uuid)
        video.status = "queued"
        video.action = 'intro'
        video.save()
    return Response()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class CustomLoginClass(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email:
            return Response(
                {"error": "Email token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not password:
            return Response(
                {"error": "Password is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_model = get_user_model()
        case_insensitive_username_field = "{}__iexact".format(
            user_model.USERNAME_FIELD
        )
        try:
            account = Account.objects.get(email=email)
            user = user_model._default_manager.get(
                **{case_insensitive_username_field: email}
            )
        except user_model.DoesNotExist and Account.DoesNotExist:
            return Response({'error': 'Credentials are incorrect!'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.check_password(password) and account.is_admin:
            auth_tokens = get_tokens_for_user(user)
            return Response(auth_tokens, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Credentials are incorrect!'}, status=status.HTTP_401_UNAUTHORIZED)


class CustomTokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate existing refresh token
            old_refresh = RefreshToken(refresh_token)
            user_id = old_refresh.payload.get('user_id')

            user_model = get_user_model()
            user = user_model.objects.get(id=user_id)
            account = Account.objects.get(id=user_id)
            if not account.is_admin:
                return Response(
                    {"error": "Invalid or expired refresh token"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Create new tokens
            new_refresh = RefreshToken.for_user(user)
            new_access = new_refresh.access_token

            return Response({
                'access': str(new_access),
                'refresh': str(new_refresh),
            }, status=status.HTTP_200_OK)

        except Exception as e:

            print(e)
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
