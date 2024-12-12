from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import (
    FavoriteRecipes, Ingredient,
    Recipe, ShoppingList,
    Subscriptions, Tag, User
)


class CookingTimeFilter(admin.SimpleListFilter):
    title = _('Время готовки')
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        # Динамическое определение порогов N и M
        all_recipes = model_admin.model.objects.all()
        n = self.get_thresholds(all_recipes)['n']
        m = self.get_thresholds(all_recipes)['m']
        return [
            ('fast', _(f'быстрее {n} мин '
                       f'({all_recipes.filter(cooking_time__lt=n).count()})')),
            ('medium', _(f'от {n} до {m} мин '
                         f'({all_recipes.filter(
                             cooking_time__gte=n, cooking_time__lt=m
                         ).count()})')),
            ('long', _(f'дольше {m} мин '
                       f'({all_recipes.filter(
                           cooking_time__gte=m
                       ).count()})')),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'fast':
            n = self.get_thresholds(queryset)['n']
            return queryset.filter(cooking_time__lt=n)
        if value == 'medium':
            thresholds = self.get_thresholds(queryset)
            return queryset.filter(
                cooking_time__gte=thresholds['n'],
                cooking_time__lt=thresholds['m']
            )
        if value == 'long':
            m = self.get_thresholds(queryset)['m']
            return queryset.filter(cooking_time__gte=m)
        return queryset

    def get_thresholds(self, queryset):
        cooking_times = queryset.values_list('cooking_time', flat=True)
        if cooking_times:
            n = (min(cooking_times) + (max(cooking_times)
                                       - min(cooking_times)) // 3)
            m = n + (max(cooking_times) - min(cooking_times)) // 3
        else:
            n, m = 10, 30
        return {'n': n, 'm': m}


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cooking_time', 'author',
        'get_tags', 'get_ingredients', 'get_image',
        'in_favorites'
    )
    list_filter = ('tags', 'author', CookingTimeFilter)

    @admin.display(description='Теги')
    def get_tags(self, recipe):
        return '\n'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        return mark_safe('<br>'.join(
            f'{ingredient.name} ({ingredient.measurement_unit}) - '
            f'{ingredient.recipe_ingredients.get(recipe=recipe).amount}'
            for ingredient in recipe.ingredients.all()
        ))

    @admin.display(description='Картинка')
    def get_image(self, recipe):
        if recipe.image:
            return mark_safe(
                f'<img src="{recipe.image.url}" '
                f'style="max-width: 200px; max-height: 200px;" />'
            )
        return "Нет изображения"

    def in_favorites(self, recipes):
        return recipes.favoriterecipes_related.count()
    in_favorites.short_description = 'В избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Количество рецептов')
    def recipes_count(self, ingredients):
        return ingredients.recipes.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug',)

    @admin.display(description='Количество рецептов')
    def recipes_count(self, tag):
        return tag.recipes.count()


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'recipe__name',)
    list_filter = ('author', 'recipe',)


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'recipe',)
    list_filter = ('author', 'recipe',)


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    list_filter = ('user', 'author',)


admin.site.register(User)
