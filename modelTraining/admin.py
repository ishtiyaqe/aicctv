from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
import os
from .models import *
from django.template.loader import get_template
from django.utils.translation import gettext as _
# Register your models here.

from ultralytics import YOLO
 
 

    
    
 
    
 

@admin.register(CameraWarningLabelList)
class CameraWarningLabelListAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CameraWarningLabelList._meta.fields]
    
class CameraWarningLabelListInline(admin.TabularInline):  # or admin.StackedInline
    model = CameraWarningLabelList
    extra = 0  # Number of extra forms to display

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Camera._meta.fields]
    inlines = [CameraWarningLabelListInline]
 
 

@admin.register(CameraWarningVideoList)
class CameraWarningVideoListAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CameraWarningVideoList._meta.fields]
 

@admin.register(CameraScreen)
class CameraScreenAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CameraScreen._meta.fields]
    


