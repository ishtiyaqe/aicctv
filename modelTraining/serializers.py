from .models import *
from xml.dom import ValidationErr
from rest_framework import serializers
# serializers.py
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate


UserModel = get_user_model()



class CameraWarningVideoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraWarningVideoList
        fields = '__all__'
        


class CameraWarningLabelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraWarningLabelList
        fields = '__all__'

class CameraSerializer(serializers.ModelSerializer):
    labels = CameraWarningLabelListSerializer(many=True, read_only=True)  # Assuming labels is a related field in the Camera model

    class Meta:
        model = Camera
        fields = ['name', 'video_source', 'user','labels']

    def create(self, validated_data):
        labels_data = validated_data.pop('labels', [])
        camera = Camera.objects.create(**validated_data)
        for label_data in labels_data:
            CameraWarningLabelList.objects.create(camera=camera, **label_data)
        return camera

        
class UserLoginSerializer(serializers.Serializer):
	username = serializers.CharField()
	password = serializers.CharField()
	##
	def check_user(self, clean_data):
		user = authenticate(username=clean_data['username'], password=clean_data['password'])
		if not user:
			raise ValidationError({'error': 'User not found'}, code=status.HTTP_404_NOT_FOUND)
		return user



class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = ('email', 'username')