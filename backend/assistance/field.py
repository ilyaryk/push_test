import base64
import imghdr
import uuid
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _

from rest_framework.fields import ImageField

DEFAULT_CONTENT_TYPE = "application/octet-stream"
ALLOWED_IMAGE_TYPES = (
    "jpeg",
    "jpg",
    "png",
    "gif"
)

EMPTY_VALUES = (None, '', [], (), {})


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension
            print(ext)

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)


        return super().to_internal_value(data)