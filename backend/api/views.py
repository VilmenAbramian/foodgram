from io import BytesIO

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
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
    FoodgramUserSerializer, IngredientSerializer,
    RecipeMiniSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, SubscriptionsSerializerFoodgram,
    TagSerializer
)
from .shopping_cart import shopping_cart
from recipes.models import (
    Ingredient, FavoriteRecipes,
    Recipe, ShoppingList, Subscriptions,
    Tag, RecipeIngredient, User
)


def redirect_to_recipe(request, pk):
    if not Recipe.objects.filter(pk=pk).exists():
        raise ValidationError(f'Рецепт с идентификатором {pk} не найден!')
    return redirect(f'/recipes/{pk}/')


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
    queryset = Recipe.objects.all().order_by('-created_at')
    pagination_class = ApiPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            raise ValidationError(
                f'Рецепт с идентификатором {pk} не найден!'
            )
        return Response({
            'short-link': f'http://{request.get_host()}/s/{pk}'
        })

    @staticmethod
    def favorite_and_cart(model, request, kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user
        if request.method == 'POST':
            _, created = model.objects.get_or_create(
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

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        return self.favorite_and_cart(ShoppingList, request, kwargs)

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        if not ShoppingList.objects.filter(author=request.user).exists():
            return Response(
                'Список покупок пуст!',
                status=status.HTTP_404_NOT_FOUND
            )
        filling_basket = RecipeIngredient.objects.filter(
            recipe__shoppinglist__author=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit', 'recipe__name'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        return FileResponse(
            BytesIO(shopping_cart(filling_basket).encode('utf-8')),
            as_attachment=True,
            filename='shop_list.txt',
            content_type='text/plain'
        )

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        return self.favorite_and_cart(FavoriteRecipes, request, kwargs)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()

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
        author = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'DELETE':
            get_object_or_404(
                Subscriptions, user=request.user, author=author
            ).delete()
            return Response(
                'Успешная отписка',
                status=status.HTTP_204_NO_CONTENT
            )
        if request.user == author:
            raise ValidationError('Подписка на себя невозможна!')
        _, created = Subscriptions.objects.get_or_create(
            user=request.user, author=author
        )
        if not created:
            raise ValidationError(
                f'Вы уже подписаны на пользователя {author}!'
            )
        return Response(SubscriptionsSerializerFoodgram(
            author, context={'request': request, }
        ).data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def subscriptions(self, request):
        '''Отобразить все подписки пользователя'''
        user_subscriptions = Subscriptions.objects.filter(
            user=self.request.user
        ).values_list('author', flat=True)
        return self.get_paginated_response(
            SubscriptionsSerializerFoodgram(
                self.paginate_queryset(
                    User.objects.filter(id__in=user_subscriptions)
                ), many=True,
                context={'request': request}
            ).data
        )

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
        serializer = FoodgramUserSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_avatar = serializer.validated_data.get('avatar')
        user.avatar = new_avatar
        user.save()
        if new_avatar is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        image_url = request.build_absolute_uri(
            request.user.avatar.url
        )
        return Response({'avatar': image_url}, status=status.HTTP_200_OK)
