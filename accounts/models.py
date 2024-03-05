
from django.db import models
from django.contrib.auth.models import User

class CustomUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,to_field='id',null=True)
    username = models.CharField(max_length=50, unique=True, )
    phone = models.CharField(max_length=11, unique=True, verbose_name='Phone Number', blank=False, help_text='Enter 11 digits phone number')


class Profile(models.Model):
    user = models.OneToOneField(User ,on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)
    