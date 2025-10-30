from django.urls import path

from Country import api_views


urlpatterns = [
    path('list', api_views.list),
    path('<str:name>', api_views.single)
]
