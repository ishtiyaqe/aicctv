import os
import threading
from time import sleep
from channels.generic.websocket import AsyncWebsocketConsumer
from .video_processor import start_video_processing
from object_detection.models import *
import json 
from channels.layers import get_channel_layer
import asyncio

rnfm = {}
# Define a function to be run in a separate thread
def start_processing_in_thread():
    start_video_processing(rnfm)
    print(rnfm)
# Create and start the thread
processing_thread = threading.Thread(target=start_processing_in_thread)
processing_thread.start()
channel_layer = get_channel_layer()


class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.camera_id = self.scope['url_route']['kwargs']['camera_id']
        self.group_name = f"video_stream_{self.camera_id}"

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # Start the loop to continuously send frames to the client
        self.update_loop_task = asyncio.create_task(self.update_loop())

       

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_frames_to_client(self):
        # Convert self.camera_id to integer type to ensure consistent comparison
        camera_id = int(self.camera_id)
        
        if camera_id in rnfm:
            frame_bytes_list = rnfm[camera_id]
            if frame_bytes_list:
                # If the key exists and the list is not empty, proceed with sending frame bytes
                # Send frame bytes over WebSocket
                for data_list in frame_bytes_list:
                    await self.send(text_data=data_list)
            else:
                print(f"No frame bytes found for camera ID: {camera_id}")
        else:
            print(f"No data found for camera ID: {camera_id}")
    
    async def update_loop(self):
        while True:
            try:
                await self.update_frame_bytes_list()
                # Wait for a while before checking for updates again
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                # Catch CancelledError when the task is cancelled due to disconnect
                break

    async def update_frame_bytes_list(self):
        camera_id = int(self.camera_id)
        if camera_id in rnfm:
            frame_bytes_list = rnfm[camera_id]
            if frame_bytes_list:
                # Store the previous data outside the loop
                previous_data_list = None
                for data_list in frame_bytes_list:
                    if previous_data_list is None or previous_data_list != data_list:
                        await self.send_frames_to_client()
                    # Update previous_data_list for the next iteration
                    previous_data_list = data_list
        else:
            print(f"No data found for camera ID: {camera_id}")


    # Call this method when you want to update frame_bytes_list
    # await self.update_frame_bytes_list()
