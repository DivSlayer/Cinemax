from django.urls import path
from Movie import views

app_name = "movie"

urlpatterns = [
    path(),
    path('<slug:slug>', views.single, name="single")
]
