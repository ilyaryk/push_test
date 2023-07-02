from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewSet, FavoriteViewSet, \
    FollowViewSet, CartViewSet, IngredientViewSet, UserViewSet, SignUpApiView, GetJWTTokenView


router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tag', TagViewSet, basename='tag')
router.register('follow', FollowViewSet, basename='follow')
router.register('favorite', FavoriteViewSet, basename='favorite')
router.register('cart', CartViewSet, basename='cart')
router.register('ingredient', IngredientViewSet, basename='ingredient')
router.register('users', UserViewSet, basename='users')
#router.register('auth/token/login', SignUpApiView, basename='signup')
#router.register('auth/token/login', GetJWTTokenView, basename='signin')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.jwt'))
]
