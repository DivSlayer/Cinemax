from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from Account import api_views, views

urlpatterns = [
    path("check-email", api_views.check_email),
    path("details", views.DetailsApi.as_view()),
    path("plans/purchase/<str:uuid>", views.PurchasePlan.as_view()),
    path("plans", views.PlansList.as_view()),
    path("register", views.RegisterUser.as_view()),
    path("token", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", views.CustomTokenRefreshView().as_view(), name="token_refresh"),
]
