import json
from django.http import HttpResponse
from Country.models import Country
from Country.serializers import CountrySerializer
from Movie.models import Movie
from Serial.models import Serial
from Utility.no_serializer import all_serializer
from Utility.responses import list_response
from Utility.tools import adv_search_filter, ordering


def single(request, name):
    all_together = []
    page = request.GET.get("page", 1)
    movies = Movie.objects.filter(country__name__in=[name])
    movies = adv_search_filter(request, movies)
    serials = Serial.objects.filter(country__name__in=[name])
    serials = adv_search_filter(request, serials)
    all_together.extend(movies)
    all_together.extend(serials)
    order = request.GET.get("order", None)
    ordered = ordering(all_together, order)
    serialized = []
    for obj in ordered:
        serialized.append(all_serializer(obj))
    return list_response(serialized, page=page, serialize=False)


def list(request):
    return HttpResponse(
        json.dumps(CountrySerializer(Country.objects.all(), many=True).data),
        content_type="application/json",
    )
