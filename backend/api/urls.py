from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet,
    FollowViewSet, CartViewSet, UserViewSet,
    IngredientViewSet, GetJWTTokenView, DeleteJWTTokenView)
from recipes.views import RecipeViewSet

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('follow', FollowViewSet, basename='follow')
router.register('cart', CartViewSet, basename='cart')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path("api/auth/token/login/", GetJWTTokenView.as_view()),
    path("api/auth/token/logout/", DeleteJWTTokenView.as_view()),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.jwt'))
]
