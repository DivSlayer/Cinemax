from django.urls import path
from Person import views

app_name = "Person"
urlpatterns = [
    path('movies',views.person_movies, name="movies"),
    path('<slug:slug>', views.index, name="index")
]
