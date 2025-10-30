from copy import deepcopy
from itertools import combinations
import pandas as pd
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from Movie.models import Movie
from Person.models import Person
from Rest.common_serializers import SmallPersonSerializer, SmallMovieSerializer
from Serial.models import Serial


@api_view(('GET', ))
@renderer_classes((JSONRenderer, ))
def search(request):
    if request.GET.get('search', None) is not None:
        persons = [person.name for person in Person.objects.all()]
        movies = [movie.title for movie in Movie.objects.filter()]
        serials = [series.title for series in Serial.objects.all()]
        together = persons + movies + serials
        searched = search_engine(request.GET.get('search'), together)
        new_format = set_search_format(searched)
        print(new_format)
        return Response({'result': new_format})
    else:
        return Response({"error": 'Search input is Empty!'})


def search_engine(search_val, old_list_str):

    def start(string, old_list):
        string = string.lower()
        results = []
        results_per = []
        if len(string.split(' ')) == 1:
            for item in old_list:
                percent = one_word_similarity(string, item.lower())
                results.append(item)
                results_per.append(percent)
        else:
            for item in old_list:
                percent = more_than_one(string, item.lower())
                results.append(item)
                results_per.append(percent)
        check_index_per = 0
        result_per_copy = deepcopy(results_per)
        result_copy = deepcopy(results)
        for value in results_per:
            if int(value) < 15:
                result_copy.pop(check_index_per)
                result_per_copy.pop(check_index_per)
            else:
                check_index_per += 1
        df = pd.DataFrame({"Movie": result_copy, "Per": result_per_copy})
        df = df.sort_values(by="Per", ascending=False)
        arr = df[["Movie"]].to_numpy()
        arr2 = [movie[0] for movie in arr]
        return arr2[:10]

    def more_than_one(string, source):
        movie_coms = get_array(source)
        if string in movie_coms:
            splitted_srearch = string.split(' ')
            indexes = []
            for word in splitted_srearch:
                indexes.append(source.split(' ').index(word))
            indexes = sorted(indexes, reverse=True)
            diffenrece = 0
            for item in indexes:
                index_item = indexes.index(item)
                if len(indexes) - 1 > index_item:
                    next_item = indexes[index_item + 1]
                    if item - next_item > 1:
                        diffenrece += item - next_item - 1
            percent = len(splitted_srearch) / (len(source.split(' ')) +
                                               diffenrece) * 100
            return percent
        else:
            total_percents = 0
            for words in string.split(' '):
                percent = one_word_similarity(words, source)
                total_percents += percent

            return total_percents

    def get_array(string):
        all_combinations = []
        for i in range(1, len(string)):
            coms = combinations(string.split(' '), i)
            for com in coms:
                all_combinations.append(" ".join(com))
        return all_combinations

    def one_word_similarity(string, source):
        movie_coms = get_array(source)
        if string in movie_coms:
            index = source.split(" ").index(string)
            splitted_source = source.split(" ")
            percent = (1 / (len(splitted_source))) * 100
            return percent
        else:
            all_percents = []
            all_indexes = []
            indexes = []
            for com in source.split(' '):
                similars = 0
                current = 0
                for letter in com:
                    if current <= len(string) - 1:
                        if letter == string[current]:
                            similars += 1
                            indexes.append(current)
                    current += 1
                percent = (similars /
                           (len(string) + len(source.replace(' ', '')) *
                            (source.split(' ').index(com) + 1))) * 100
                index = source.split(' ').index(com)
                all_percents.append(percent)
                all_indexes.append(index)
            differs = 0
            for item in indexes:
                index_item = indexes.index(item)
                if len(indexes) - 1 > index_item:
                    next_item = indexes[index_item + 1]
                    if item - next_item > 1:
                        differs += item - next_item - 1
            max = sorted(all_percents, reverse=True)[0]
            final_percent = (max / (len(source.split(' ')) + differs))
            return final_percent

    return start(search_val, old_list_str)


def set_search_format(datas):
    datas = list(dict.fromkeys(datas))
    new_form = []
    for item in datas:
        persons = Person.objects.filter(name=item)
        movie = Movie.objects.filter(title=item)
        serials = Serial.objects.filter(title=item)
        if len(persons) > 0:
            serializer = SmallPersonSerializer(persons[0], many=False)
            new_form.append(serializer.data)
        if len(movie) > 0:
            serializer = SmallMovieSerializer(movie[0], many=False)
            new_form.append(serializer.data)
        if len(serials) > 0:
            serializer = SmallMovieSerializer(serials[0], many=False)
            new_form.append(serializer.data)
    return new_form
