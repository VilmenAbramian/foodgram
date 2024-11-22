from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .filters import RecipeFilter
from .paginations import ApiPagination
from .serializers import (
    IngredientSerializer,
    RecipeMiniSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer
)
from recipes.models import Ingredient, Recipe, ShoppingList, Tag
from users.models import User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = ApiPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def partial_update(self, request, *args, **kwargs):
        obj = get_object_or_404(Recipe, pk=kwargs['pk'])

        if 'ingredients' not in request.data:
            return Response(
                {'ingredients': 'Это обязательное поле!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'tags' not in request.data:
            return Response(
                {'tags': 'Это обязательное поле!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user != Recipe.objects.get(id=kwargs['pk']).author:
            return Response(
                {'users': 'Нельзя редактировать чужую запись!'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)
    
    @action(detail=True,
            methods=['get'],
            url_path='get-link'
        )
    def get_link(self, *args, **kwargs):
        return Response(
            {'short-link': f'https://example.com/recipes/{kwargs}'}
        )
    
    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        user = self.request.user
        if ShoppingList.objects.filter(
            author=user, recipe=recipe
        ).exists():
            return Response(
                'Рецепт уже добавлен!',
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = RecipeMiniSerializer(recipe)
        ShoppingList.objects.create(author=user, recipe=recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        author = User.objects.get(id=request.user.pk)
        if author.shopping_list.exists():
            return 'Make me'
        return Response(
            'Список покупок пуст!',
            status=status.HTTP_404_NOT_FOUND
        )
