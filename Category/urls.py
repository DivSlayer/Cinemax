from django.urls import path
from Category import views

app_name = "category"

urlpatterns = [
    path('movie/<str:title>', views.movies, name="movies"),
    path('<str:title>', views.index, name="index")
]
