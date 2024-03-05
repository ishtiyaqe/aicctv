# admin.py
from django.contrib import admin
from .models import *



@admin.register(NewModelTrainingStatus)
class NewModelTrainingStatusAdmin(admin.ModelAdmin):
    list_display = [field.name for field in NewModelTrainingStatus._meta.fields]


@admin.register(DownloadedFile)
class DownloadedFileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DownloadedFile._meta.fields]


@admin.register(RunNumberOfTest)
class RunNumberOfTestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RunNumberOfTest._meta.fields]


@admin.register(Trained_model)
class Trained_modelAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Trained_model._meta.fields]