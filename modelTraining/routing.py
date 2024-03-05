# routing.py
from django.urls import re_path
from .consumers import VideoStreamConsumer

websocket_urlpatterns = [
    re_path(r'ws/video_stream/(?P<camera_id>\d+)/$', VideoStreamConsumer.as_asgi()),
]
