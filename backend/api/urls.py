from django.urls import include, path
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet
from api.views import CustomUserViewSet


router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='user')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken'))
]
