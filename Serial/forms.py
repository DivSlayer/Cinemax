from django import forms
from Serial.models import Episode, EpisodeSubtitle, Serial


class CreateEpisode(forms.ModelForm):
    class Meta:
        model = Episode
        fields = ["number", "serial", "season", "video"]


class CreateSerial(forms.ModelForm):
    class Meta:
        model = Serial
        fields = ["imdb_id", "title"]


class CreateEpisodeSub(forms.ModelForm):
    class Meta:
        model = EpisodeSubtitle
        fields = ["srt", "vtt", "episode"]
