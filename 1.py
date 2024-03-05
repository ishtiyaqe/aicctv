# views.py

from django.shortcuts import render
from django.http import JsonResponse
import requests

def start_stream(request):
    # Start a new stream on the RTMP server
    rtmp_server_url = 'http://localhost:8000/live'
    response = requests.post(rtmp_server_url, data={})
    if response.status_code == 200:
        return JsonResponse({'message': 'Stream started successfully'})
    else:
        return JsonResponse({'error': 'Failed to start stream'}, status=500)

def stop_stream(request):
    # Stop the currently running stream on the RTMP server
    rtmp_server_url = 'http://localhost:8000/live'
    response = requests.post(rtmp_server_url, data={})
    if response.status_code == 200:
        return JsonResponse({'message': 'Stream stopped successfully'})
    else:
        return JsonResponse({'error': 'Failed to stop stream'}, status=500)
