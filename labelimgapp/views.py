# labelimgapp/views.py
from django.shortcuts import render

def labelimg(request):
    return render(request, 'labelimg.html')

def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        # Handle image upload and save it
        image = request.FILES['image']
        # Save image and return response
    else:
        # Handle GET request or invalid POST request
        # Return appropriate response or redirect
