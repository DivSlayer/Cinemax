from django import forms

from Movie.models import Subtitle, Movie


class CreateMovieSubtitle(forms.ModelForm):
    class Meta:
        model = Subtitle
        fields = ['srt']


class CreateMovie(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['imdb_id', 'title', 'franchise']
