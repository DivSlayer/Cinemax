import json
import math

from django.shortcuts import render

from Movie.models import Subtitle, Audio, Movie, Subtitle
from Serial.models import Serial
from Utility.adv_search import AdvanceSearch
from Utility.tools import ordering

def version_2(request, slug=None):
    return render(request, 'v2/index.html')

def home(request, slug=None):
    page = request.GET.get('page', 1)
    order = request.GET.get('order', '-rating')
    page = int(page)
    adv_instance = AdvanceSearch(request)
    all_together = adv_instance.initialize()
    ordered = ordering(all_together, order=order)
    first_int = (page - 1) * 20
    last_int = page * 20
    main_list = ordered[first_int:last_int]
    subbed = []
    dubbed = []
    for subtitle in Subtitle.objects.all():
        if subtitle.movie not in subbed:
            subbed.append(subtitle.movie)
    for audio in Audio.objects.all():
        if audio.movie not in dubbed:
            dubbed.append(audio.movie)
    context = {
        'main': main_list,
        'subbed_list': subbed,
        'dubbed_list': dubbed,
        'page': page,
        'last_page': math.ceil(len(ordered) / 20),
        'first_page': 1,
        'min_year': Movie.objects.all().order_by('year').first().year,
        'max_year': Movie.objects.all().order_by('-year').first().year,
    }
    for item in adv_instance.values:
        print(f'item: {item}, value:{adv_instance.values[item]}')
        context[item] = adv_instance.values[item]
    return render(request, 'home.html', context=context)
