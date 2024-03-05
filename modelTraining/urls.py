from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.decorators.csrf import csrf_exempt
from .views import *

urlpatterns = [
    path('api/login/', UserLogin.as_view(), name='login'),
	path('api/logout/', UserLogout.as_view(), name='logout'),
	path('api/user/', UserView.as_view(), name='user'),
    path('api/user_profiles/', UserProfileViews.as_view(), name='user-profiles'),
    path('api/cameras/', CameraCreateView.as_view(), name='camera-create'),
    path('cameras/', CameraListView.as_view(), name='camera-list'),
    path('camera-warning-videos/<int:camera_id>/', CameraWarningVideoListView.as_view(), name='camera-warning-videos'),
    path('warning-images/', CameraWarningVideoLists.as_view(), name='warning-images'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)