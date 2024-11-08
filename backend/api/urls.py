from django.urls import include, path, re_path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken'))
]