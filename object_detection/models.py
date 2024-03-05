from django.db import models
from roboflow import Roboflow
from django.utils import timezone

class DownloadedFile(models.Model):
    rf = models.CharField(max_length=255,null=True,help_text='Roboflow(api_key="FPridAEvD8w9kQzE3Jih")')
    project = models.CharField(max_length=255,null=True,help_text='rf.workspace("test-x8w2c").project("protection-detaction")')
    dataset = models.CharField(max_length=255,null=True,help_text='project.version(1).download("yolov8")')
    project_name = models.CharField(max_length=255,null=True)
    project_version = models.IntegerField(max_length=255,null=True)

class Trained_model(models.Model):
    Test_name = models.CharField(max_length=255,null=True)
    Trained_model = models.FileField(upload_to="static/labels/", null=True, blank=True)
    active = models.BooleanField(default=False)  # Boolean field for active status
    updated = models.DateTimeField(auto_now=True)  # Date and time when the data is updated (auto-updated)
    created_at = models.DateTimeField(default=timezone.now)  # Date and time when the data is created

    def __str__(self):
        return f"Trained Model {self.id}"

class RunNumberOfTest(models.Model):
    count = models.IntegerField(max_length=255,null=True,help_text='100')

class NewModelTrainingStatus(models.Model):
    Test_name = models.CharField(max_length=255)
    status = models.CharField(max_length=255)