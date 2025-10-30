from Movie.models import Movie, Franchise, Subtitle as MovieSubtitle, Video
from Movie.serializers import MovieSerializer
from Person.models import Person
from Person.serializers import PersonSerializer
from Rest.common_serializers import SmallPersonSerializer, SmallSerialSerializer, SmallMovieSerializer
from Serial.models import Serial, Episode, Season, EpisodeSubtitle, SeasonSubtitle
from Serial.serializers import EpisodeSerializer, SeasonSerializer, SerialSerializer


def all_serializer(obj, small=False, item_img=False, vitals=False):
    if type(obj) == Movie:
        return MovieSerializer(obj).data if not small else SmallMovieSerializer(obj).data
    if type(obj) == Serial:
        return SerialSerializer(obj).data if not small else SmallSerialSerializer(obj).data
    if type(obj) == Person:
        return PersonSerializer(obj).data if not small else SmallPersonSerializer(obj).data
    if type(obj) == Episode:
        return EpisodeSerializer(obj).data
    if type(obj) == Season:
        return SeasonSerializer(obj).data


def get_object(imdb_id, use_imdb=True, use_slug=False):
    if use_imdb:
        try:
            movie = Movie.objects.get(imdb_id=imdb_id)
            return movie
        except:
            pass
        try:
            series = Serial.objects.get(imdb_id=imdb_id)
            return series
        except:
            pass
        try:
            serial = Serial.objects.get(imdb_id=imdb_id)
            return serial
        except:
            pass
        try:
            actor = Person.objects.get(imdb_id=imdb_id)
            return actor
        except:
            pass
    elif use_slug:
        try:
            print(f'movie slug: {imdb_id}')
            movie = Movie.objects.get(slug=imdb_id)
            return movie
        except Exception as e:
            print(e)
            pass
        try:
            series = Serial.objects.get(slug=imdb_id)
            return series
        except:
            pass

        try:
            series = Person.objects.get(slug=imdb_id)
            return series
        except:
            pass

    else:
        try:
            movie = Movie.objects.get(uuid=imdb_id)
            return movie
        except:
            pass
        try:
            movie = Video.objects.get(uuid=imdb_id)
            return movie
        except:
            pass
        try:
            series = Serial.objects.get(uuid=imdb_id)
            return series
        except:
            pass
        try:
            franchise = Franchise.objects.get(uuid=imdb_id)
            return franchise
        except:
            pass
        try:
            person = Person.objects.get(uuid=imdb_id)
            return person
        except:
            pass
        try:
            episode = Episode.objects.get(uuid=imdb_id)
            return episode
        except:
            pass
        try:
            season = Season.objects.get(uuid=imdb_id)
            return season
        except:
            pass

        try:
            movie_sub = MovieSubtitle.objects.get(uuid=imdb_id)
            return movie_sub
        except:
            pass

        try:
            episode_sub = EpisodeSubtitle.objects.get(uuid=imdb_id)
            return episode_sub
        except:
            pass
        try:
            season_sub = SeasonSubtitle.objects.get(uuid=imdb_id)
            return season_sub
        except:
            return None
