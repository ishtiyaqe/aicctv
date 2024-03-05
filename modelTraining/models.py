from enum import unique
from django.db import models
from django.contrib.auth.models import User


    

class Camera(models.Model):
    name = models.CharField(max_length=100, unique=True)
    video_source = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name

class CameraScreen(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, null=True)
    last_image = models.BinaryField(blank=True, null=True)
    last_video_source = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.camera.name} - {self.id}"
    
class CameraWarningVideoList(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    image = models.FileField(upload_to='Warning/images/', null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    labels = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class CameraWarningLabelList(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)