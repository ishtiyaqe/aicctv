# your_django_app/utils.py
import base64
from django.http import StreamingHttpResponse

def generate_frames(camera_screen):
    while True:
        with camera_screen.frame_lock:
            frame = camera_screen.frame_data.get("frame")

        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
