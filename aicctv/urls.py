
from django.contrib import admin
from django.urls import path, include
from modelTraining.admin import *

urlpatterns = [
    path("", include("modelTraining.urls")),
    path("", include("object_detection.urls")),
    path('admin/', admin.site.urls),
    # path('labelimg/', include('labelimgapp.urls')),
    
]



