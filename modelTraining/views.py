import cv2
import asyncio
from django.http import HttpResponse
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Camera
from ultralytics import YOLO
import time
import threading
import logging
import decimal
from django.shortcuts import get_object_or_404
from django.contrib import messages
import os
import re
import time
from cmath import exp
from decimal import *
from http.client import EXPECTATION_FAILED
# from importlib.resources import path
from multiprocessing import context
from urllib import request
# from attrs import attr
import requests
import datetime
from django.conf import settings
import re


from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError
from django.db.models import Avg, Count, Max, Min
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
# paypal
from django.urls import URLPattern, reverse
from django.views.decorators.csrf import csrf_exempt
# required imports
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from rest_framework.settings import api_settings
from rest_framework.test import APIClient
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view
import uuid
import json
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import generics
from .serializers import *
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.core.serializers import serialize
from urllib.parse import urlparse
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import status, permissions, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.generics import CreateAPIView




class UserProfileViews(APIView):
    def get(self, request):
        # Check if the user is logged in
        if request.user.is_authenticated:

            return Response("User profile  found", status=status.HTTP_200_OK)

        else:
            return Response("User not logged in", status=status.HTTP_401_UNAUTHORIZED)
     
      
class CameraWarningVideoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, camera_id):
        camera_warning_videos = CameraWarningVideoList.objects.filter(camera=camera_id)
        serializer = CameraWarningVideoListSerializer(camera_warning_videos, many=True)
        return Response(serializer.data)
    
      
from django.db.models import Count

class CameraWarningVideoLists(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the user is an admin
        if request.user.is_staff:
            cameras = Camera.objects.all()
        else:
            cameras = Camera.objects.filter(user=request.user)

        grouped_data = []
        for camera in cameras:
            camera_warning_videos = CameraWarningVideoList.objects.filter(camera=camera)
            data = {
                'camera_name': camera.name,
                'images': CameraWarningVideoListSerializer(camera_warning_videos, many=True).data
            }
            grouped_data.append(data)

        return Response(grouped_data)

      
        
class CameraListView(APIView):
    def get(self, request):
        # Check if the user is an admin
        if request.user.is_staff:
            cameras = Camera.objects.all()
        else:
            cameras = Camera.objects.filter(user=request.user)
        pmd = []
        for camera in cameras:
            data = {
                    'camera_name': camera.name,
                    'camera_ids': camera.id 
                }
            pmd.append(data)
        return Response(pmd, status=status.HTTP_200_OK)
    
    
    

class CameraCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Extract data from the request
        name = request.data.get('name')
        video_source = request.data.get('video_source')
        labels_data = request.data.get('labels', [])
        user = request.user.id

        # Serialize the camera data
        camera_serializer = CameraSerializer(data={'name': name, 'video_source': video_source,'user': user})

        # Serialize the label data
        label_serializers = [CameraWarningLabelListSerializer(data={'name': label}) for label in labels_data]

        if camera_serializer.is_valid() and all(label_serializer.is_valid() for label_serializer in label_serializers):
            # Save the camera instance
            camera_instance = camera_serializer.save()

            # Save the labels instances
            for label_serializer in label_serializers:
                label_serializer.save(camera=camera_instance)

            return Response({'message': 'Camera and labels created successfully'}, status=status.HTTP_201_CREATED)
        else:
            errors = {
                'camera_errors': camera_serializer.errors,
                'label_errors': [label_serializer.errors for label_serializer in label_serializers]
            }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        serializer = UserLoginSerializer(data=data)
        if not username or not password:
            return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.check_user(data)

        if user is not None:
            login(request, user)
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            error_message = 'User not found'
            return JsonResponse({'error': error_message}, status=404)

class UserLogout(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def post(self, request):
		logout(request)
		return Response(status=status.HTTP_200_OK)

class UserView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	authentication_classes = (SessionAuthentication,)
	##
	def get(self, request):
		serializer = UserSerializer(request.user)
		return Response({'user': serializer.data}, status=status.HTTP_200_OK)



# Initialize YOLO model outside the loop
yolo_model = None
running_frames = {}
logger = logging.getLogger(__name__)

class VideoStream:
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.latest_frame = None
        self.latest_detection_data = None
        self.processed_frames_count = 0
        threading.Thread(target=self.generate_frames_sync, args=()).start()

    def get_camera(self):
        return Camera.objects.get(id=self.camera_id)

    def generate_frames_sync(self):
        global yolo_model

        try:
            camera = self.get_camera()
            video_capture = cv2.VideoCapture('hardhat.mp4')
        
            while True:
                success, frame = video_capture.read()

                if not success:
                    break

                if yolo_model is None:
                    yolo_model = YOLO("best.pt")

                predictions = yolo_model(frame)

                for i in range(predictions[0].boxes.xyxy.shape[0]):
                    x1, y1, x2, y2 = predictions[0].boxes.xyxy[i, :4]
                    class_label = predictions[0].names[int(predictions[0].boxes.cls[i])]

                    color = (0, 0, 255) if 'NO-Safety' in class_label or 'NO-Mask' in class_label else (0, 255, 0)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    label_text = f"{class_label}"
                    cv2.putText(frame, label_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                _, buffer = cv2.imencode('.jpeg', frame)
                frame_bytes = buffer.tobytes()

                self.latest_frame = frame_bytes
                self.latest_detection_data = predictions
                running_frames[self.camera_id] = frame_bytes

                # Sleep removed to allow for real-time streaming
                # time.sleep(3)

        except Exception as e:
            logger.error(f"Error in frame generation: {e}")
            time.sleep(5)

class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.camera_id = self.scope['url_route']['kwargs']['camera_id']
        self.room_group_name = f'video_stream_{self.camera_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        pass

    # Stream video frames to the client
    async def stream_frame(self, event):
        try:
            camera = self.get_camera()
            video_capture = cv2.VideoCapture('hardhat.mp4')
        
            while True:
                success, frame = video_capture.read()

                if not success:
                    break

                if yolo_model is None:
                    yolo_model = YOLO("best.pt")

                predictions = yolo_model(frame)

                for i in range(predictions[0].boxes.xyxy.shape[0]):
                    x1, y1, x2, y2 = predictions[0].boxes.xyxy[i, :4]
                    class_label = predictions[0].names[int(predictions[0].boxes.cls[i])]

                    color = (0, 0, 255) if 'NO-Safety' in class_label or 'NO-Mask' in class_label else (0, 255, 0)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    label_text = f"{class_label}"
                    cv2.putText(frame, label_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                _, buffer = cv2.imencode('.jpeg', frame)
                frame_bytes = buffer.tobytes()

                self.latest_frame = frame_bytes
                self.latest_detection_data = predictions
                running_frames[self.camera_id] = frame_bytes
                await self.send(text_data=frame_bytes)

                # Sleep removed to allow for real-time streaming
                # time.sleep(3)

        except Exception as e:
            logger.error(f"Error in frame generation: {e}")
            time.sleep(5)


        # Send frame to WebSocket