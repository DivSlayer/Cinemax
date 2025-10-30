from django.urls import path
from Serial import api_views

urlpatterns = [
    path('top', api_views.top_serials),
    path('list', api_views.main_list),

]
