from django.urls import path

from Serial import views

app_name = "serial"
urlpatterns = [
    path('<slug:slug>', views.single, name="single")
]
