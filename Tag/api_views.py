import json

from django.conf import settings
from django.http import HttpResponse
from Movie.models import Movie
from Serial.models import Serial
from Tag.models import Tag
from Utility.responses import list_response
from Utility.tools import ordering

Server = settings.SITE_URL

def list_tags(request):
    datas = []
    for tag in Tag.objects.all():
        movies = [movie for movie in Movie.objects.filter(tags__en_title__in=[tag.en_title])]
        serials = [serial for serial in Serial.objects.filter(tags__en_title__in=[tag.en_title])]
        all_together = []
        all_together.extend(movies)
        all_together.extend(serials)
        ordered = ordering(all_together)
        new_form = {
            "en_title": tag.en_title,
            "fa_title": tag.fa_title,
            "icon" : tag.icon,
            "url" : tag.url,
            "poster": Server + ordered[0].poster_img.url if len(ordered) > 0 else ""

        }
        datas.append(new_form)
    return HttpResponse(json.dumps(datas), content_type='application/json')

def single(request, url):
    page = request.GET.get('page',1)
    page = int(page)
    try:
        tag = Tag.objects.get(url=url)
        movies = [movie for movie in Movie.objects.filter(tags__en_title__in=[tag.en_title])]
        serials = [serial for serial in Serial.objects.filter(tags__en_title__in=[tag.en_title])]
        all_together = []
        all_together.extend(movies)
        all_together.extend(serials)
        ordered = ordering(all_together)
        pagined = list_response(ordered, page=page,small=True)
        return pagined
    except Exception as e:
        # raise e
        return HttpResponse(json.dumps({"error": 'Something went wrong!'}),status=400)