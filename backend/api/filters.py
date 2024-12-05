import django_filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag
from recipes.models import User


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']

    def filter_is_in_shopping_cart(self, recipes, name, value):
        if self.request.user.is_authenticated and value:
            return recipes.filter(shopping_list__author=self.request.user)
        return recipes

    def filter_is_favorited(self, recipes, name, value):
        if self.request.user.is_authenticated and value:
            return recipes.filter(favorite__author=self.request.user)
        return recipes
