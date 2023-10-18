from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from recipes.models import Recipe, Favorite
from api.serializers import RecipeInSubscribeSerializer

def favorite_or_cart(self, model, id):
    objects = model.objects.filter(
        user=self.request.user,
        recipe=get_object_or_404(Recipe, id=id))

    fav_flag = objects.exists()
    if self.request.method == "POST":
        if fav_flag:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        model.objects.create(user=self.request.user,
                             recipe=get_object_or_404(Recipe, id=id))
        serializer =  RecipeInSubscribeSerializer(Recipe.objects.get(id=id))
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if not fav_flag:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    objects.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


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