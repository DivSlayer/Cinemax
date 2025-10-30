"""
URL configuration for Cinemax project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('h=', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from Cinemax import views
from Cinemax import settings

urlpatterns = [
    path("api/", include("Rest.urls")),
    path("tool/", include("Tool.urls")),
    path("upload/", include("Upload.urls")),
    path('movie/', views.version_2),
    path('serial/', views.version_2),
    path('player/', views.version_2),
    path("category/", views.version_2),
    path('person/', views.version_2),
    path('play/<slug:slug>', views.version_2),
    path("admin/", admin.site.urls),
    path("dashboard/", include("Dashboard.urls")),
    path("movie/<slug:slug>", views.version_2),
    path("serial/<slug:slug>", views.version_2),
    path("category/<slug:slug>", views.version_2),
    path("genre/<slug:slug>", views.version_2),
    path("search", views.version_2),
    path("", views.version_2),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)