from django.contrib import admin
from Serial.models import Serial, Audio, SeasonSubtitle, EpisodeSubtitle, Trailer, Episode, Season

admin.site.register(Serial)
admin.site.register(Season)
admin.site.register(Episode)
admin.site.register(Trailer)
admin.site.register(Audio)
admin.site.register(SeasonSubtitle)
admin.site.register(EpisodeSubtitle)
