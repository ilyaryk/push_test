from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from recipes.models import Recipe


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
        return Response(status=status.HTTP_201_CREATED)
    if not fav_flag:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    objects.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
