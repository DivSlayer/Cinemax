import mimetypes
import os
import re
from wsgiref.util import FileWrapper

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from Account.models import Account
from Movie.models import Movie, Video
from Utility.responses import list_response, paginator
from Utility.tools import adv_search_filter, ordering
from Utility.no_serializer import all_serializer
from django.http import HttpResponse, FileResponse
import json
import math


def top_movies(request):
    movies = Movie.objects.all().order_by('-rating')[:5]
    page = request.GET.get('page', 1)
    return list_response(arr=movies, page=page, small=True)


def main_list(request):
    all_together = []
    page = request.GET.get("page", 1)
    page = int(page)
    movies = Movie.objects.all()
    movies = adv_search_filter(request, movies)
    all_together.extend(movies)
    order = request.GET.get("order", None)
    ordered = ordering(all_together, order)
    return list_response(ordered, page=page, small=True, item_img=True)

