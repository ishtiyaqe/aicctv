import threading
import os
import cv2
import time
from django.conf import settings
from .models import *
from object_detection.models import *
from pytube import YouTube
from channels.layers import get_channel_layer
from django.core.files.base import ContentFile
from ultralytics import YOLO
import base64


channel_layer = get_channel_layer()
yolo_model = None

def get_camera_ids():
    return list(Camera.objects.values_list('id', flat=True))

def get_active_model():
    return Trained_model.objects.filter(active=True).last().Trained_model

def get_camera_labels(camera):
    ld = []
    ls = CameraWarningLabelList.objects.filter(camera=camera)
    for i in ls:
        ld.append(i.name)
    return ld

def save_video(camera, class_label, frames):
    # Generate image title
    image_title = f"red_boxes_{time.strftime('%Y-%m-%d_%H-%M-%S')}"

    # Create directory to save images if it doesn't exist
    output_dir = os.path.join(settings.MEDIA_ROOT, 'images')
    os.makedirs(output_dir, exist_ok=True)

    # Concatenate all frames vertically to form a single image
    combined_frame = cv2.vconcat(frames)

    # Save the combined frame as an image file
    image_path = os.path.join(output_dir, f'{image_title}.jpeg')
    cv2.imwrite(image_path, combined_frame)

    # Save metadata to database
    CameraWarningVideoList.objects.create(
        camera=camera,
        name=image_title,
        labels=class_label,
        image=image_path
    )
    
    
def save_frame_as_image(frame, camera_id, labels):
    camera = Camera.objects.get(id=camera_id)
    image_instance = save_frames_as_images(camera=camera, name=f"frame_{timezone.now().strftime('%Y%m%d%H%M%S')}", end_time=timezone.now(), labels=labels)
    image_instance.image.save(f"{timezone.now().strftime('%Y%m%d%H%M%S')}.jpg", ContentFile(cv2.imencode('.jpg', frame)[1].tobytes()))
pls = 0
def process_video(camera_id, rnfm):
    global pls
    pls += 1
    print(pls)
    if camera_id not in rnfm:
        rnfm[camera_id] = []  
    camera = Camera.objects.get(id=camera_id)
    active_model = get_active_model()
    trained_model_path = active_model.path
    print(f"Processing video for camera ID: {camera_id}")
    print(f"Processing video for path: {trained_model_path}")

    yolo_model = YOLO(trained_model_path)

    youtube_url = camera.video_source
    yt = YouTube(youtube_url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    stream_url = stream.url

    video_capture = cv2.VideoCapture(stream_url)
    camera_labels = get_camera_labels(camera)
    start_time = time.time()
    frame_buffer = []  # Buffer to store frames for 10 seconds

    while True:
        success, frame = video_capture.read()

        if not success:
            break

        predictions = yolo_model(frame)
        red_box =  False
        for i in range(predictions[0].boxes.xyxy.shape[0]):
            x1, y1, x2, y2 = predictions[0].boxes.xyxy[i, :4]
            class_label = predictions[0].names[int(predictions[0].boxes.cls[i])]

            color = (0, 0, 255) if any(label in class_label for label in camera_labels) else (0, 255, 0)
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            label_text = f"{class_label}"
            cv2.putText(frame, label_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            frame_buffer.append(frame)
            if any(label in class_label for label in camera_labels):
                red_box =True
            if red_box:
                save_video(camera, class_label, frame)
                # Save frame as image
                # save_frame_as_image(frame, camera_id, label_text)

        _, buffer = cv2.imencode('.jpeg', frame)
        frame_bytes = buffer.tobytes()

                # Encode the frame bytes to Base64 string
        frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
        rnfm[camera_id] =[]
        rnfm[camera_id].append(frame_base64)

        # Send the frame to WebSocket consumer
        channel_layer.group_send(f"video_stream_{camera_id}", {"type": "send_frame", "frame_bytes": frame_bytes})

def start_video_processing(rnfm):
    global yolo_model
    camera_ids = get_camera_ids()
    threads = {}

    while True:
        for camera_id in camera_ids:
            if camera_id not in threads or not threads[camera_id].is_alive():
                # If the thread is not running, start it
                print(f"Starting video processing for camera ID: {camera_id}")
                threads[camera_id] = threading.Thread(target=process_video, args=(camera_id, rnfm))
                threads[camera_id].start()

        # Sleep for a certain duration before checking again
        time.sleep(5)  # Adjust the duration as needed




