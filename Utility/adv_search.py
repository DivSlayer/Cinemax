import math

from Movie.models import Movie, Subtitle as MovieSub, Audio
from Serial.models import Serial


class AdvanceSearch:
    def __init__(self, request, main_list=None) -> None:
        self.request = request
        self.values = {
            'resolution': 0,
            'year_max': 100,
            'year_min': 0,
            'rate_min': 10,
            'rate_max': 100,
            'dubbed': 'off',
            'subbed': 'off',
        }
        self.default_vals = {
            'resolution': '0',
            'year_max': 100,
            'year_min': 0,
            'rate_min': 10,
            'rate_max': 100,
            'dubbed': 'off',
            'subbed': 'off',
        }
        self.funcs = {
            'resolution': self.filter_res,
            'year_max': self.year_max_filter,
            'year_min': self.year_min_filter,
            'rate_max': self.rate_max_filter,
            'rate_min': self.rate_min_filter,
            'dubbed': self.dubbed_filter,
            'subbed': self.subbed_filter
        }
        self.main_list = main_list

    def initialize(self):
        if self.main_list is None:
            self.main_list = []
            movies = [movie for movie in Movie.objects.all()]
            serials = [serial for serial in Serial.objects.all()]
            self.main_list.extend(movies)
            self.main_list.extend(serials)
        req_min_rate = float(self.request.GET.get('rate_min', 10))
        req_max_rate = float(self.request.GET.get('rate_max', 100))
        req_values = {
            'resolution': self.request.GET.get('resolution', '0'),
            'year_max': int(self.request.GET.get('year_max', 100)),
            'year_min': int(self.request.GET.get('year_min', 0)),
            'rate_min': 10 if req_min_rate == 0 else req_min_rate,
            'rate_max': 10 if req_max_rate == 0 else req_max_rate,
            'dubbed': self.request.GET.get('dubbed', 'off'),
            'subbed': self.request.GET.get('subbed', 'off')
        }
        for value in req_values:
            if req_values[value] != self.default_vals[value]:
                print(value)
                self.main_list = self.funcs[value](req_values[value])
        return self.main_list

    def filter_res(self, res):
        returning = []
        self.values['resolution'] = res
        for movie in self.main_list:
            if movie.resolution == res:
                returning.append(movie)
        return returning

    def year_max_filter(self, max_v):
        self.values['year_max'] = max_v
        returned = []
        max_year = int(Movie.objects.all().order_by('-year').first().year)
        min_year = int(Movie.objects.all().order_by('year').first().year)
        differ = max_year - min_year
        percent_year = math.ceil(differ * max_v / 100)
        max_year = min_year + percent_year
        for movie in self.main_list:
            if int(movie.year) <= max_year:
                returned.append(movie)
        return returned

    def year_min_filter(self, min_v):
        self.values['year_min'] = min_v
        returned = []
        max_year = int(Movie.objects.all().order_by('-year').first().year)
        min_year = int(Movie.objects.all().order_by('year').first().year)
        differ = max_year - min_year
        percent_year = math.ceil(differ * min_v / 100)
        min_year = min_year + percent_year
        for movie in self.main_list:
            if int(movie.year) >= min_year:
                returned.append(movie)
        return returned

    def rate_max_filter(self, max_rate):
        self.values['rate_max'] = 10 if max_rate < 10 else max_rate
        returned = []
        wanted_max = float(max_rate) / 10
        for movie in self.main_list:
            if float(movie.rating) <= wanted_max:
                returned.append(movie)
        return returned

    def rate_min_filter(self, min_v):
        self.values['year_min'] = 10 if min_v < 10 else min_v
        returned = []
        wanted_min = float(min_v) / 10
        for movie in self.main_list:
            if float(movie.rating) >= wanted_min:
                returned.append(movie)
        return returned

    def subbed_filter(self, value):
        self.values['subbed'] = 'on'
        returned = []
        for movie in self.main_list:
            if type(movie) == Movie:
                subs = MovieSub.objects.filter(movie=movie)
                if len(subs) > 0:
                    returned.append(movie)
        return returned

    def dubbed_filter(self, value):
        self.values['dubbed'] = 'on'
        returned = []
        for movie in self.main_list:
            if type(movie) == Movie:
                audios = Audio.objects.filter(movie=movie)
                if len(audios) > 0:
                    returned.append(movie)
        return returned
