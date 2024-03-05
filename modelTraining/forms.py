from django import forms
from django.core.validators import validate_image_file_extension
from django.utils.translation import gettext as _
from multiupload.fields import MultiFileField, MultiMediaField, MultiImageField

from .models import *

