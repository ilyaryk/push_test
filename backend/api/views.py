import io

from rest_framework import viewsets, permissions, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.db.models import Sum
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from recipes.models import (Recipe, Favorite, Cart, Ingredient,
                            Tag, Follow, AmountOfIngredient)
from .serializers import (RecipeCreateOrUpdateSerializer,
                          RecipeReadOnlySerializer,
                          TagSerializer,
                          IngredientSerializer,
                          FollowSerializer,
                          UserSerializer,
                          UserReadOnlySerializer,
			  RecipeInSubscribeSerializer,
			  UserAnonSerializer,
			  RecipeAnonSerializer)
from .permissions import IsAuthorOrReadOnly
from assistance.pagination import CustomPagination
from users.models import User
from assistance.utils import favorite_or_cart


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    #serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            if self.request.user.is_anonymous:
                return UserAnonSerializer
            return UserReadOnlySerializer
        return UserSerializer


    @action(detail=False, url_path='me', methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_path='subscribe', methods=('post', 'delete'),
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, pk):
        user = request.user
        following = get_object_or_404(User, id=pk)
        change_subscription_status = Follow.objects.filter(
            user=user.id, following=following.id)
        sub_status = change_subscription_status.exists()
        if request.method == 'POST':
            if sub_status:
                return Response({'detail': 'Уже подписаны!'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, following=following).save()
            data = UserReadOnlySerializer(following,
                                          context={'request': request}).data
            return Response(data,
                            status=status.HTTP_201_CREATED)
        if sub_status:
            change_subscription_status.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Такой подписки нет'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, url_path='subscriptions', methods=('get',),
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        if queryset.exists():
            queryset_pag = self.paginate_queryset(queryset)
            serializer = UserReadOnlySerializer(
                queryset_pag, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        return Response({'detail': 'Подписок нет'},
                        status=status.HTTP_400_BAD_REQUEST)



from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django_filters import rest_framework as filters
from django.db.models import Q
import json

import django_filters

class RecipeFilter(django_filters.FilterSet):
    '''class Meta:
        model = Recipe
        fields = ['tags__slug']'''
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )



class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly)
    pagination_class = CustomPagination
    #filter_backends = [filters.SearchFilter]
    #search_fields = ['tags__slug']

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    #filterset_fields = ('tags__slug',)
    def get_serializer_class(self):
        if self.request.user.is_anonymous:
                return RecipeAnonSerializer
        if self.request.method == 'GET':
            return RecipeReadOnlySerializer
        return RecipeCreateOrUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    '''def get_queryset(self):
        data = Recipe.objects.all()
        if (not self.request.user.is_anonymous):
            if self.request.GET.get('is_favorited') == "1":
                data = data.filter(fav__user=self.request.user)
            if self.request.GET.get('is_in_shopping_cart') == "1":
                data = data.filter(recipe__user=self.request.user)
        if self.request.GET.get('author'):
            data = data.filter(author__id=self.request.GET.get('author'))
        #if self.request.GET.get('tags'):
        #    data = data.filter(tags__slug__in=[self.request.GET.get('tags')])
        return (data)'''

    @action(detail=True, url_path='favorite', methods=('post', 'delete'),
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        return favorite_or_cart(self, Favorite, pk)

    @action(detail=True, url_path='shopping_cart', methods=('post', 'delete'),
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return favorite_or_cart(self, Cart, pk)

    @action(detail=False, url_path='download_shopping_cart', methods=('get',),
            permission_classes=(permissions.IsAuthenticated,))
    def download(self, request):
        buffer = io.BytesIO()
        pdfmetrics.registerFont(TTFont(name='arial', filename='assistance/font/Cyrillic/arial.TTF'))
        p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
        textob = p.beginText()
        textob.setTextOrigin(inch, inch)
        textob.setFont("arial", 14)
        objs = (
            AmountOfIngredient.objects.filter(
                recipe__in=list(request.user.buyer.values_list(
                    'recipe',
                    flat=True)),)).select_related('recipes').values(
                    'ingredient__name',
                    'ingredient__measurement_unit',).annotate(
                        summa=Sum('amount'))
        for obj in objs:
            line_out = (str(obj['ingredient__name']) + ' '
                        + str(obj['ingredient__measurement_unit']) + ' '
                        + str(obj['summa']))
            textob.textLine(line_out.encode("utf-8"))
        p.drawText(textob)
        p.showPage()
        p.save()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename="venue.pdf")


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    pagination_class = None
    serializer_class = IngredientSerializer
    def get_queryset(self):
        queryset = Ingredient.objects.filter(name__istartswith=self.request.GET.get('name'))
        return queryset
