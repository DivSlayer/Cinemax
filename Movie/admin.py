from django.contrib import admin
from Movie.models import Movie, Trailer, Audio, Franchise, Subtitle, Video


class MyModelAdmin(admin.ModelAdmin):
    # To order ascending by 'priority' and descending by 'created_at'
    ordering = ['-last_update']


admin.site.register(Movie)
admin.site.register(Trailer)
admin.site.register(Franchise)
admin.site.register(Video,MyModelAdmin)
admin.site.register(Audio)
admin.site.register(Subtitle)
