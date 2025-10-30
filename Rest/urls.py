from django.urls import path, include
from Rest import views
from Rest.adv_search import advanced_search

app_name = "REST"
urlpatterns = [
    path("movie/", include("Movie.api_urls")),
    path("serial/", include("Serial.api_urls")),
    path("tag/", include("Tag.api_urls")),
    path("genre/", include("Category.api_urls")),
    path("dashboard/", include("Dashboard.api_urls")),
    path("country/", include("Country.api_urls")),
    path("lists/", include("Lists.api_urls")),
    path("account/", include("Account.api_urls")),
    path("main-list", views.main_list),
    path("adv-search", advanced_search),
    path("latest", views.latest, name="latest"),
    path("posters", views.posters, name="posters"),
    path("single", views.single, name="single"),
    path("search", views.search),
    path("error", views.error),
    path("vitals", views.vitals),
    path("fix", views.fix),
    path("update/<str:slug>", views.manual_update),
    path("get-source", views.GetSourceLink.as_view()),
    path("stream/<str:uuid>", views.StreamVideo.as_view()),
    path("download/<str:uuid>", views.DownloadVideo.as_view(),name="download"),
    path('forbidden', views.get_forbidden),
    path('all', views.get_all),
]
