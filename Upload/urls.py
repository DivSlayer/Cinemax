from django.urls import path, include
from Upload import views

urlpatterns = [
    path('episode', views.episode),
    path('movie', views.movie, name="movie"),
    path('serial', views.serial)
]
 