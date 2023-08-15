import io

from rest_framework import viewsets, permissions, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from recipes.models import (Recipe, Favorite, Cart, Ingredient,
                            Tag, Follow, AmountOfIngredients)
from .serializers import (RecipeCreateOrUpdateSerializer,
                          RecipeReadOnlySerializer,
                          TagSerializer,
                          IngredientSerializer,
                          FollowSerializer,
                          UserSerializer)
from .permissions import IsAuthorOrReadOnly
from assistance.pagination import CustomPagination
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

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
            data = UserSerializer(following).data
            data.update({
                'id': following.id,
                'is_subscribed': Follow.objects.filter(
                    user=user,
                    following=following).exists(),
                'recipies': Recipe.objects.filter(author=following),
                'recipies_count':
                    (Recipe.objects.filter(author=following).count())
            })
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
        queryset = Follow.objects.filter(user=request.user)
        if queryset.exists():
            queryset_pag = self.paginate_queryset(queryset)
            serializer = FollowSerializer(
                queryset_pag, context={'request': request}, many=True,)
            return self.get_paginated_response(serializer.data)
        return Response({'detail': 'Подписок нет'},
                        status=status.HTTP_400_BAD_REQUEST)


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

    def get_queryset(self):
        data = Recipe.objects.all()
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
            fav_objects = Favorite.objects.filter(
                user=request.user,
                recipe=get_object_or_404(Recipe, id=pk)
                                                 )
            if fav_objects.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=request.user,
                                    recipe=get_object_or_404(Recipe, id=pk)
                                    )
            return Response(status=status.HTTP_201_CREATED)
        if not fav_objects.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        fav_objects.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='shopping_cart', methods=('post', 'delete'),
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            cart_objects = Cart.objects.filter(
                user=request.user,
                item=get_object_or_404(Recipe, id=pk)
                                              )
            if cart_objects.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Cart.objects.create(user=request.user,
                                item=get_object_or_404(Recipe, id=pk)
                                )
            return Response(status=status.HTTP_201_CREATED)
        if not cart_objects.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        cart_objects.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='download_shopping_cart', methods=('get',),
            permission_classes=(permissions.IsAuthenticated,))
    def download(self, request):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
        textob = p.beginText()
        textob.setTextOrigin(inch, inch)
        textob.setFont("Helvetica", 14)
        lines = {}
        recipes = Recipe.objects.filter(item__user=self.request.user)
        for recipe in recipes:
            amounts = AmountOfIngredients.objects.filter(recipe=recipe)
            for amount in amounts:
                if lines.get(amount.ingredient.__str__()):
                    lines[amount.ingredient.__str__()] = (
                        lines.get(amount.ingredient.__str__()) + amount.amount)
                else:
                    lines[amount.ingredient.__str__()] = amount.amount
        for line in lines.keys():
            line_out = str(line) + str(lines[line])
            textob.textLine(line_out)
        p.drawText(textob)
        p.showPage()
        p.save()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename="venue.pdf")


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly)
    pagination_class = LimitOffsetPagination


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
