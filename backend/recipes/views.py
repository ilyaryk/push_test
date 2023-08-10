import io
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import FileResponse
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Recipe
from recipes.models import Favorite, Cart
from api.permissions import IsAuthorOrReadOnly
from .serializers import (RecipeCreateOrUpdateSerializer,
                          RecipeReadOnlySerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadOnlySerializer
        return RecipeCreateOrUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return Response(status=status.HTTP_201_CREATED)

    def get_queryset(self):
        data = Recipe.objects.all()
        print(data.first().ingredients)
        if self.request.GET.get('is_favorited') == "1":
            data = data.filter(fav__user=self.request.user)
        if self.request.GET.get('is_in_shopping_cart') == "1":
            data = data.filter(item__user=self.request.user)
        if self.request.GET.get('author'):
            data = data.filter(author__id=self.request.GET.get('author'))
        if self.request.GET.get('tags'):
            data = data.filter(tags__in=[self.request.GET.get('tags')])
        return (data)

    @action(detail=True, url_path='favorite', methods=('post', 'delete'),
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        if request.method == "POST":
            if Favorite.objects.filter(user=request.user,
                                       recipe=get_object_or_404(Recipe, id=pk)
                                       ).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=request.user,
                                    recipe=get_object_or_404(Recipe, id=pk)
                                    )
            return Response(status=status.HTTP_201_CREATED)
        if not Favorite.objects.filter(user=request.user,
                                       recipe=get_object_or_404(Recipe, id=pk)
                                       ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.filter(user=request.user,
                                recipe=get_object_or_404(Recipe, id=pk)
                                ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='shopping_cart', methods=('post', 'delete'),
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            if Cart.objects.filter(user=request.user,
                                   item=get_object_or_404(Recipe, id=pk)
                                   ).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Cart.objects.create(user=request.user,
                                item=get_object_or_404(Recipe, id=pk)
                                )
            return Response(status=status.HTTP_201_CREATED)
        if not Cart.objects.filter(user=request.user,
                                   item=get_object_or_404(Recipe, id=pk)
                                   ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Cart.objects.filter(user=request.user,
                            recipe=get_object_or_404(Recipe, id=pk)
                            ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='download_shopping_cart', methods=('get',),
            permission_classes=(permissions.IsAuthenticated,))
    def download(self, request):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
        textob = p.beginText()
        textob.setTextOrigin(inch, inch)
        textob.setFont("Helvetica", 14)
        recipies = Recipe.objects.filter(item__user=self.request.user)
        lines = []
        for recipe in recipies:
            ingredients = recipe.ingredients.all()
            for ingredient in ingredients:
                lines.append(ingredient.__str__())
        lines = set(lines)
        for line in lines:
            textob.textLine(line)
        p.drawText(textob)
        p.showPage()
        p.save()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename="venue.pdf")