from collections import defaultdict

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
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
from recipes.models import (
    Ingredient, FavoriteRecipes,
    Recipe, ShoppingList, Tag
)
from users.models import User


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user
                or request.user.is_superuser)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = ApiPagination
    permission_classes = (IsOwnerOrAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def partial_update(self, request, *args, **kwargs):
        get_object_or_404(Recipe, pk=kwargs['pk'])

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
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True,
            methods=['get'],
            url_path='get-link')
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
        if request.method == 'POST':
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
        if request.method == 'DELETE':
            shopping_item = ShoppingList.objects.filter(
                author=user, recipe=recipe
            ).first()
            if not shopping_item:
                return Response(
                    {'error': 'Рецепт не найден в корзине!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            shopping_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        author = User.objects.get(id=request.user.pk)
        if author.shopping_list.exists():
            shopping_list = shopping_cart(request, author)
            return Response(
                shopping_list,
                status=status.HTTP_200_OK
            )
        return Response(
            'Список покупок пуст!',
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            if FavoriteRecipes.objects.filter(
                author=user, recipe=recipe
            ).exists():
                return Response(
                    'Рецепт уже существует!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipes.objects.create(author=user, recipe=recipe)
            return Response(
                RecipeMiniSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        favorite = FavoriteRecipes.objects.filter(author=user, recipe=recipe)
        if not favorite.exists():
            return Response(
                {'error': 'Рецепт не найден в избранном!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(
            {'message': 'Рецепт удалён из избранного!'},
            status=status.HTTP_204_NO_CONTENT
        )


def shopping_cart(request, author):
    shopping_list = ShoppingList.objects.filter(author=author)
    recipes = [item.recipe for item in shopping_list]
    all_ingredients = defaultdict(float)
    for recipe in recipes:
        for recipe_ingredient in recipe.recipe_ingredients.all():
            ingredient = recipe_ingredient.ingredient
            all_ingredients[(
                ingredient.name, ingredient.measurement_unit
            )] += recipe_ingredient.amount

    text_version = '\n'.join(
        f'{name} - {amount} ({unit})'
        for (name, unit), amount in all_ingredients.items()
    )

    return text_version
