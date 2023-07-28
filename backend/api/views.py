import io
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, views
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.http import FileResponse
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .pagination import CustomPagination
from .models import Recipe, Tag, Favorite, Follow, Cart, Ingredient, User
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    RecipeSerializer, TagSerializer,
    FollowSerializer, CartSerializer, IngredientSerializer,
    UserSerializer, SignUpSerializer, GetJWTTokenSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly)
    pagination_class = LimitOffsetPagination

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


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly)
    pagination_class = LimitOffsetPagination


class FollowViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsAuthorOrReadOnly)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.request.user.buyer.all()


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


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
        if request.method == 'POST':
            if change_subscription_status.exists():
                return Response({'detail': 'Уже подписаны!'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, following=following).save()
            data1 = {
                'id': following.id,
                'is_subscribed': Follow.objects.filter(
                    user=user,
                    following=following).exists(),
                'recipies': Recipe.objects.filter(author=following),
                'recipies_count':
                    (Recipe.objects.filter(author=following).count())
            }
            data = UserSerializer(following).data
            data.update(data1)
            return Response(data,
                            status=status.HTTP_201_CREATED)
        if change_subscription_status.exists():
            change_subscription_status.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Такой подписки нет'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, url_path='subscriptions', methods=('get',),
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        if queryset:
            queryset_pag = self.paginate_queryset(queryset)
            serializer = FollowSerializer(
                queryset_pag, context={'request': request}, many=True,)
            return self.get_paginated_response(serializer.data)
        return Response({'detail': 'Подписок нет'},
                        status=status.HTTP_400_BAD_REQUEST)


class SignUpApiView(views.APIView):
    """User registration."""

    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        return Response(status=status.HTTP_200_OK)


class GetJWTTokenView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GetJWTTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, password=serializer.data.get("password"),
            email=serializer.data.get("email")
        )
        refresh = RefreshToken.for_user(user)

        return Response(
            {"token": str(refresh.access_token)},
            status=status.HTTP_201_CREATED,
        )


class DeleteJWTTokenView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GetJWTTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, password=serializer.data.get("password"),
            email=serializer.data.get("email")
        )
        RefreshToken.for_user(user)

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
