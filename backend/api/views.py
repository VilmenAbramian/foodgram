from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import TagSerializer
from recipes.models import Tag

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    ...


class RecipeViewSet(viewsets.ModelViewSet):
    ...
