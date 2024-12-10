from datetime import date
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .paginations import ApiPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    CustomUserSerializer, IngredientSerializer,
    RecipeMiniSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, SubscriptionsSerializer,
    TagSerializer
)
from recipes.models import (
    Ingredient, FavoriteRecipes,
    Recipe, ShoppingList, Subscriptions,
    Tag, RecipeIngredient, User
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = ApiPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(detail=True, url_path='get-link')
    def get_link(self, *args, **kwargs):
        try:
            site_url = settings.ALLOWED_HOSTS[3]
        except IndexError:
            site_url = 'localhost'
        short_link = f'{site_url}/recipes/{kwargs.get("pk")}'
        return Response({'short-link': short_link})

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        return favorite_and_cart(ShoppingList, request, kwargs)

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        author = User.objects.get(id=request.user.pk)
        if ShoppingList.objects.filter(author=author).exists():
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
    def favorite(self, request, **kwargs):
        return favorite_and_cart(FavoriteRecipes, request, kwargs)


def favorite_and_cart(model, request, kwargs):
    recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
    user = request.user
    if request.method == 'POST':
        object, created = model.objects.get_or_create(
            author=user, recipe=recipe
        )
        if not created:
            raise ValidationError(
                {'detail': 'Уже добавлено!'}
            )
        return Response(
            RecipeMiniSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )
    if request.method == 'DELETE':
        get_object_or_404(model, author=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def shopping_cart(request, author):
    ingredients = RecipeIngredient.objects.filter(
        recipe__shoppinglist_related__author=author
    ).values(
        'ingredient__name', 'ingredient__measurement_unit', 'recipe__name'
    ).annotate(
        total_amount=Sum('amount')
    )
    header = f"Список покупок от {date.today().strftime('%d.%m.%Y')}"
    products = 'Список ингредиентов\n:' + '\n'.join([
        f'{i + 1}) {ingredient["ingredient__name"].capitalize()} - '
        f'{ingredient["total_amount"]} '
        f'{ingredient["ingredient__measurement_unit"]}'
        for i, ingredient in enumerate(ingredients)
    ])
    recipes_set = set(
        [(ingredient['recipe__name']) for ingredient in ingredients]
    )
    recipes = 'Список рецептов:\n' + '\n'.join([
        f'{i + 1}) {recipe.capitalize()}'
        for i, recipe in enumerate(recipes_set)
    ])
    return '\n'.join([
        header,
        products,
        recipes
    ])
    # return ingredients


class CustomUserViewSet(UserViewSet):
    def get_queryset(self):
        return User.objects.all()

    @action(detail=False,
            methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        return super().me(request)

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        '''Создать и/или удалить подписку'''
        author = get_object_or_404(User, id=kwargs.get('id'))
        recipes_limit = int(request.GET.get('recipes_limit', 10**10))
        if request.method == 'POST':
            if recipes_limit is not None:
                recipes_limit = int(recipes_limit)
            if self.request.user == author:
                raise ValidationError('Подписка на себя невозможна!')
            subscription, created = Subscriptions.objects.get_or_create(
                user=self.request.user,
                author=author
            )
            if not created:
                raise ValidationError(
                    'Вы уже подписаны на этого пользователя!'
                )
            serializer = SubscriptionsSerializer(
                author, context={'request': request, 'limit': recipes_limit}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(Subscriptions, author=author).delete()
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

        user_subscriptions = Subscriptions.objects.filter(
            user=self.request.user
        ).values_list('author', flat=True)

        authors = User.objects.filter(id__in=user_subscriptions)
        pages = self.paginate_queryset(authors)
        serializer = SubscriptionsSerializer(
            pages, many=True,
            context={'request': request, 'limit': recipes_limit}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=('put', 'delete'),
            permission_classes=(IsAuthenticated,))
    def avatar(self, request, *args, **kwargs):
        '''Добавить или изменить аватар пользователя'''
        user = self.request.user
        if request.method == 'DELETE':
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(
                'Изображение профиля успешно удалено',
                status=status.HTTP_204_NO_CONTENT
            )
        serializer = CustomUserSerializer(data=request.data, partial=True)
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
