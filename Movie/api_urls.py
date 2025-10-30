from django.urls import path

from Movie import api_views

app_name = "movie_api"
urlpatterns = [
    path('top', api_views.top_movies),
    path('list', api_views.main_list)
]
