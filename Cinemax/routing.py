from django.urls import re_path

from Movie import consumers

websocket_urlpatterns = [
    re_path( r'^ws/progress/(?P<uuid>[^/]+)$', consumers.VideoProcessingConsumer.as_asgi()),
]