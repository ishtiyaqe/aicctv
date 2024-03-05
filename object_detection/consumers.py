import asyncio
import cv2
import json
import base64
import pafy
from urllib.parse import urlparse
from channels.generic.websocket import AsyncWebsocketConsumer
from ultralytics import YOLO
from django.db import close_old_connections
from channels.generic.websocket import WebsocketConsumer

yolo_model = YOLO("best.pt")

class ObjectDetectionConsumer(WebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        video_source = text_data.strip()
        await self.detect_objects(video_source)

    async def detect_objects(self, video_source):
        close_old_connections()
        if urlparse(video_source).scheme:
            video = pafy.new(video_source)
            best_stream = video.getbest(preftype="mp4")
            video_source = best_stream.url

        video_capture = cv2.VideoCapture(video_source)

        try:
            while True:
                success, frame = video_capture.read()

                if not success:
                    break

                predictions = yolo_model(frame)

                if predictions[0].boxes.xyxy.numel() > 0:
                    for i in range(predictions[0].boxes.xyxy.shape[0]):
                        x1, y1, x2, y2 = predictions[0].boxes.xyxy[i, :4]
                        class_index = int(predictions[0].boxes.cls[i])
                        confidence = float(predictions[0].boxes.conf[i])
                        class_label = predictions[0].names[class_index]

                        if 'NO-Safety' in class_label or 'NO-Mask' in class_label:
                            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                            label_text = f"{class_label}: {confidence:.2f}"
                            cv2.putText(frame, label_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        else:
                            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                            label_text = f"{class_label}: {confidence:.2f}"
                            cv2.putText(frame, label_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                _, buffer = cv2.imencode('.png', frame)
                frame_bytes = buffer.tobytes()
                frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')

                await self.send(text_data=json.dumps({"frame": frame_base64}))

                # Introduce a small delay to avoid the loop consuming too much CPU
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            pass
        finally:
            video_capture.release()
