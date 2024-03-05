# urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # path('start_stream/', views.start_stream, name='start_stream'),
    path('model_train/', views.train_yolo, name='model_train'),
    path('', views.index, name='/'),
    path('download-training-data/', views.execute_command_page, name='download-training-data'),
    path('admin/logout/', views.custom_logout, name='custom_logout'),
    path('account_logout/', views.account_logout, name='account_logout'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
]
