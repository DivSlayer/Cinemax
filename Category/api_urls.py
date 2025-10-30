from django.urls import path

from Category import api_views

urlpatterns = [
    path('list', api_views.list_genre),
    path('<str:title>', api_views.single)
]
