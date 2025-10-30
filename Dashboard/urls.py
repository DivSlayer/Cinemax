from django.urls import path

from Dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name="home"),
    path('<slug:slug>', views.index, name="home"),
    # path('upload-movie', views.movie, name="movie"),
    # path('upload-franchise', views.franchise, name="franchise"),
    # path('upload-serial', views.serial, name="serial"),
    # path('upload-season', views.season, name="season"),
    # path('upload-episode', views.episode, name="episode"),
    # path('upload-movie-subtitle', views.movie_sub, name="movie-sub"),
    # path('upload-season-subtitle', views.season_sub, name="season-sub"),
    # path('upload-episode-subtitle', views.episode_sub, name="episode-sub"),
    # path('data-movies', views.data_movies, name="data-movies"),
    # path('data-serial', views.data_serial, name="data-serial"),
    # path('data-seasons', views.data_seasons, name="data-seasons"),
    # path('data-episodes', views.data_episodes, name="data-episodes"),
    # path('data-movies-sub', views.data_movies_sub, name="data-movies-sub"),
    # path('data-episodes-sub',
    #      views.data_episodes_sub,
    #      name="data-episodes-sub"),
    # path('delete-episodes',
    #      views.delete_object,
    #      name="delete"),
    # path('get-soft',
    #      views.get_soft,
    #      name="get-soft"),
    # path('check-status',
    #      views.check_status,
    #      name="check-status"),
    # path('get-audios',
    #      views.get_audios,
    #      name="get-audios"),
]