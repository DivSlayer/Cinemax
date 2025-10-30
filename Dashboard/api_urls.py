from django.urls import path
from Dashboard import api_views


urlpatterns = [
    path('home',api_views.HomePage.as_view()),
    path("check-videos/<str:uuid>", api_views.check_videos),
    path("check-images/<str:uuid>", api_views.check_images),
    path("check-subs/<str:uuid>",api_views.check_subs),
    path("censor/<str:uuid>", api_views.censor),
    path("credits/<str:uuid>", api_views.credits),
    path("add-soft/<str:uuid>", api_views.add_soft),
    path('cancel-action/<str:uuid>',api_views.cancel_action),
    path('add-intro/<str:uuids>',api_views.add_intro),

    path('token',api_views.CustomLoginClass.as_view()),
    path('token/refresh',api_views.CustomTokenRefreshView.as_view()),
]
