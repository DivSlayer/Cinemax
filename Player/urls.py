from django.urls import path

from Player import views

app_name = "player"

urlpatterns = [
    path('details/<str:uuid>', views.online_details, name="details"),
    path('<str:uuid>', views.online, name="online"),
]
