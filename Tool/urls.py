from django.urls import path

from Tool import views


urlpatterns=[
    path('poster/<str:imdb_id>', views.get_poster)
]