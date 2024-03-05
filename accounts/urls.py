from django.conf import settings
from django.urls import include, path
from django.contrib import admin
# from home import models

from .models import *
from .views import *


urlpatterns = [
    path('accounts/login/' , login_attempt , name="login"),
    path('otp' , otp , name="otp"),
    path('login-otp', login_otp , name="login_otp") ,
    path('resend-otp/<str:mobile>', resend_otp , name="resend_otp") ,
    path('accounts/', include('django.contrib.auth.urls')),
]
    
    
    
    
    
    
    
    
    
