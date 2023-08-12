from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, IngredientViewSet,
    GetJWTTokenView, DeleteJWTTokenView)
from recipes.views import RecipeViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')


urlpatterns = [
   # path("api/auth/token/login/", GetJWTTokenView.as_view()),
    #path("api/auth/token/logout/", DeleteJWTTokenView.as_view()),
    path('api/', include(router.urls)),
#    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken'))
]
