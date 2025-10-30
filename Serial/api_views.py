from Serial.models import Serial
from Utility.responses import list_response, single_response
from Utility.no_serializer import get_object, all_serializer
from Utility.tools import adv_search_filter, ordering
import math
import json
from django.http import HttpResponse

def top_serials(request):
    movies = Serial.objects.all().order_by('-rating')[:5]
    page = request.GET.get('page', 1)
    return list_response(arr=movies, page=page, small=True)

def main_list(request):
    all_together = []
    page = request.GET.get("page",1)
    page = int(page)
    serials = Serial.objects.all()
    movies = adv_search_filter(request, serials)
    all_together.extend(movies)
    order = request.GET.get("order", None)
    ordered = ordering(all_together, order)
    return list_response(ordered, page=page,small=True,item_img=True)
