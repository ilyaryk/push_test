from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewSet, FavoriteViewSet, \
    FollowViewSet, CartViewSet, IngredientViewSet


router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tag', TagViewSet)
router.register('follow', FollowViewSet, basename='follow')
router.register('favorite', FavoriteViewSet)
router.register('cart', CartViewSet)
router.register('ingredient', IngredientViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt'))
]
