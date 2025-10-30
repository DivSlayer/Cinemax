from django.urls import path

from Tag import api_views

urlpatterns = [
    path('list', api_views.list_tags),
    path('<str:url>', api_views.single)
]
