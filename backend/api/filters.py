import django_filters

from recipes.models import Recipe, Tag
from users.models import User


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all())
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    class Meta:
        model = Recipe
        fields = ['author', 'tags']