from django.shortcuts import render

from Movie.views import get_suggestions, get_related
from Serial.models import Serial, EpisodeSubtitle
from Utility.responses import error_response


# Create your views here.


def single(request, slug):
    serial = Serial.objects.filter(slug=slug)
    if len(serial) != 0:
        serial = serial.first()
        suggestions = []
        related = []
        context = {
            "serial": serial,
            'suggestions': suggestions,
            'related': related,
        }
        return render(request, 'serial.html', context=context)
    else:
        return error_response("Movie not found!", 404)
