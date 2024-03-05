
from django.urls import re_path

from .consumers import *

websocket_urlpatterns = [
    re_path("ws/detect_objects/", ObjectDetectionConsumer.as_asgi()),
]