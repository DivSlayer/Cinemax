from django.urls import path

from Lists import api_views


urlpatterns = [
    path("create", api_views.create_list),
    path("item/create/<str:uuid>", api_views.create_item),
    path("item/<str:uuid>/done", api_views.item_done),
    path("item/<str:uuid>", api_views.get_item),
    path("<str:name>/done", api_views.list_done),
    path("<str:name>", api_views.get_list),
    path("", api_views.get_lists),
]
