import os

# 1) Tell Django where your settings live
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cinemax.settings')

# 2) Immediately initialize Django and get the ASGI app
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# 3) Now it’s safe to import Channels and your routing
from channels.routing import ProtocolTypeRouter, URLRouter
import Cinemax.routing          # <-- routing may import consumers/models

application = ProtocolTypeRouter({
    "http": django_asgi_app,     # HTTP gets served by Django
    "websocket": URLRouter(
        Cinemax.routing.websocket_urlpatterns
    ),
})
