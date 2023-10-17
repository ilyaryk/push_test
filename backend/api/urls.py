from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static

from .views import TagViewSet, IngredientViewSet, RecipeViewSet, UserViewSet


router = DefaultRouter()


router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
#    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
 #   static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 