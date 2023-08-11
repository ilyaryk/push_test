from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, views
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

from recipes.models import Follow, Cart, User
from recipes.models import Ingredient, Tag
from assistance.permissions import IsAuthorOrReadOnly
from recipes.serializers import (
    TagSerializer,
    FollowSerializer, CartSerializer, IngredientSerializer)
from assistance.serializers import SignUpSerializer, GetJWTTokenSerializer


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
