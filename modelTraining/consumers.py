from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import cv2
import asyncio
from .models import *
from object_detection.models import *
from ultralytics import YOLO
import logging
import base64
from pytube import YouTube
import time
from django.utils import timezone
import os
from django.conf import settings




# Initialize YOLO model outside the loop
yolo_model = None
running_frames = {}
logger = logging.getLogger(__name__)

class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"WebSocket CONNECT requested: {self.scope['client'][0]}")
        self.camera_id = self.scope['url_route']['kwargs']['camera_id']
        self.room_group_name = f'video_stream_{self.camera_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info("WebSocket CONNECT accepted.")

        # Start video processing
        await self.start_video_processing()

    async def disconnect(self, close_code):
        logger.info(f"WebSocket DISCONNECT requested: {self.scope['client'][0]}")
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info("WebSocket DISCONNECT completed.")

    async def start_video_processing(self):
        try:
            camera = await sync_to_async(Camera.objects.get)(id=self.camera_id)
            active_model = await sync_to_async(Trained_model.objects.filter(active=True).last)()
            trained_model_path = active_model.Trained_model.path
            youtube_url = camera.video_source  # Example YouTube video URL
            yt = YouTube(youtube_url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            stream_url = stream.url  # Get the best available video stream URL
            video_capture = cv2.VideoCapture(stream_url)
            yolo_model = YOLO(trained_model_path)  # Initialize YOLO model outside the loop
            
            camera_labels_qs = await sync_to_async(CameraWarningLabelList.objects.filter)(camera=camera)
            camera_labels = await sync_to_async(list)(camera_labels_qs.values_list('name', flat=True))

            frames_with_red_boxes = []
            start_time = time.time()
            
            while True:
                success, frame = await sync_to_async(video_capture.read)()

                if not success:
                    break

                predictions = yolo_model(frame)
                red_box_found = False
                for i in range(predictions[0].boxes.xyxy.shape[0]):
                    x1, y1, x2, y2 = predictions[0].boxes.xyxy[i, :4]
                    class_label = predictions[0].names[int(predictions[0].boxes.cls[i])]

                    color = (0, 0, 255) if any(label in class_label for label in camera_labels) else (0, 255, 0)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    label_text = f"{class_label}"
                    cv2.putText(frame, label_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    if any(label in class_label for label in camera_labels):
                        red_box_found = True
                if red_box_found:
                    frames_with_red_boxes.append(frame)
                else:
                    if frames_with_red_boxes:
                        # Convert frames to video
                        end_time = time.time()
                        elapsed_time = end_time - start_time
                        image_title = f"red_boxes_{time.strftime('%Y-%m-%d_%H-%M-%S')}"
                        await save_frames_as_images(frames_with_red_boxes, image_title, camera, elapsed_time, class_label)

                        # Reset frames_with_red_boxes and start_time
                        frames_with_red_boxes = []
                        start_time = time.time()

                _, buffer = cv2.imencode('.jpeg', frame)
                frame_bytes = buffer.tobytes()

                # Encode the frame bytes to Base64 string
                frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')

                # Send the Base64 string to the client
                await self.send(text_data=frame_base64)

                # Sleep removed to allow for real-time streaming
                await asyncio.sleep(0.1)  # Adjust the sleep interval as needed

        except Exception as e:
            logger.error(f"Error in frame generation: {e}")

@sync_to_async
def save_frames_as_images(frames, title, camera, elapsed_time, labels):
    # Create directory to save images if it doesn't exist
    output_dir = os.path.join(settings.MEDIA_ROOT, 'images', title)
    os.makedirs(output_dir, exist_ok=True)

    # Save each frame as an image file
    for i, frame in enumerate(frames):
        image_path = os.path.join(output_dir, f'{title}_{i}.jpeg')
        cv2.imwrite(image_path, frame)

    # Save metadata to database
    CameraWarningVideoList.objects.create(
        camera=camera,
        name=title,
        start_time=timezone.now(),
        end_time=timezone.now() + timezone.timedelta(seconds=elapsed_time),
        labels=labels,
        image=image_path
    )

    logger.info(f"Frames for '{title}' saved as images. Elapsed time: {elapsed_time} seconds.")
