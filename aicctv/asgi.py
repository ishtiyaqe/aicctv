# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import modelTraining.routing  # Import your routing configuration

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aicctv.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Default Django HTTP handling
    # WebSocket handler
    "websocket": AuthMiddlewareStack(
        URLRouter(
            modelTraining.routing.websocket_urlpatterns
        )
    ),
})
