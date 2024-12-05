from collections import defaultdict
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
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
    SubscriptionsSerializer,
    TagSerializer
)
from recipes.models import (
    Ingredient, FavoriteRecipes,
    Recipe, ShoppingList, Tag
)
from recipes.models import Subscriptions, User
from recipes.serializers import CreateUserSerializer, UserSerializer


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


class MyPagePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = MyPagePagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    @action(detail=False,
            methods=['get', 'post'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        '''Получить свой профиль'''
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        '''Изменить пароль'''
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
            return Response(
                'Пароль успешно изменён',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        '''Создать и/или удалить подписку'''
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        recipes_limit = request.query_params.get('recipes_limit', None)
        if request.method == 'POST':
            if recipes_limit is not None:
                recipes_limit = int(recipes_limit)
            if self.request.user == author:
                return Response(
                    'Подписка на себя невозможна!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscriptions.objects.filter(
                user=self.request.user, author=author
            ).exists():
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscriptions.objects.create(user=self.request.user, author=author)
            serializer = SubscriptionsSerializer(
                author, context={'request': request, 'limit': recipes_limit}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not Subscriptions.objects.filter(
                user=self.request.user, author=author
            ).exists():
                return Response(
                    'Нельзя отписаться от несуществующей подписки!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscriptions.objects.get(author=author).delete()
            return Response(
                'Успешная отписка',
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False)
    def subscriptions(self, request):
        '''Отобразить все подписки пользователя'''
        recipes_limit = request.query_params.get('recipes_limit', None)
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)

        subscriptions = Subscriptions.objects.filter(user=self.request.user)
        user_subscriptions = [
            subscription.author for subscription in subscriptions
        ]
        pages = self.paginate_queryset(user_subscriptions)
        serializer = SubscriptionsSerializer(
            pages, many=True,
            context={'request': request, 'limit': recipes_limit}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['get', 'post', 'put', 'delete'],
            permission_classes=[IsAuthenticated])
    def avatar(self, request, *args, **kwargs):
        '''Добавить или изменить аватар пользователя'''
        user = self.request.user
        if request.method == 'DELETE':
            return Response(
                'Изображение профиля успешно удалено',
                status=status.HTTP_204_NO_CONTENT
            )
        serializer = UserSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_avatar = serializer.validated_data.get('avatar')
        user.avatar = new_avatar
        user.save()
        if new_avatar is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        image_url = request.build_absolute_uri(
            request.user.avatar.url
        )
        return Response({'avatar': str(image_url)}, status=status.HTTP_200_OK)