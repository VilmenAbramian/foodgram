from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    FavoriteRecipes, Ingredient,
    Recipe, ShoppingList,
    Subscriptions, Tag, User
)


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        # Определение диапазонов времени готовки
        all_recipes = model_admin.model.objects.all()
        all_cooking_times = all_recipes.values_list('cooking_time', flat=True)
        minimum_time, maximum_time = (
            min(all_cooking_times), max(all_cooking_times)
        )

        medium_threshold = minimum_time + (maximum_time - minimum_time) // 3
        long_threshold = medium_threshold + (maximum_time - minimum_time) // 3

        ranges = [
            ((None, medium_threshold), f'Быстро (< {medium_threshold} мин)'),
            ((medium_threshold, long_threshold),
             f'Средне (от {medium_threshold} до {long_threshold} мин)'),
            ((long_threshold, None), f'Долго (> {long_threshold} мин)'),
        ]
        return [
            (f'{lower}-{upper}', label)
            for (lower, upper), label in ranges
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        lower, upper = value.split('-')
        lower = None if lower == 'None' else int(lower)
        upper = None if upper == 'None' else int(upper)
        if lower is not None and upper is not None:
            return queryset.filter(cooking_time__range=(lower, upper))
        if lower is not None:
            return queryset.filter(cooking_time__gte=lower)
        return queryset.filter(cooking_time__lte=upper)


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
        return mark_safe('<br>'.join(tag.name for tag in recipe.tags.all()))

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        return mark_safe('<br>'.join(
            f'{item.ingredient.name} '
            f'({item.ingredient.measurement_unit}) - {item.amount}'
            for item in recipe.recipe_ingredients.select_related('ingredient')
        ))

    @admin.display(description='Картинка')
    def get_image(self, recipe):
        return (
            mark_safe(f'<img src="{recipe.image.url}" '
                      f'style="max-width: 200px; max-height: 200px;" />')
            if recipe.image
            else ''
        )

    @admin.display(description='В избранном')
    def in_favorites(self, recipe):
        return recipe.favoriterecipes.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Рецепты')
    def recipes_count(self, ingredient):
        return ingredient.recipes.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug',)

    @admin.display(description='Рецепты')
    def recipes_count(self, tag):
        return tag.recipes.count()


@admin.register(ShoppingList, FavoriteRecipes)
class ShoppingListFavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'recipe__name',)
    list_filter = ('author', 'recipe',)


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    list_filter = ('user', 'author',)


@admin.register(User)
class FoodgramUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'full_name', 'email', 'avatar_display',
        'recipes_count', 'subscriptions_count', 'subscribers_count'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')

    @admin.display(description='ФИО')
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Аватар', ordering='avatar')
    def avatar_display(self, user):
        return mark_safe(
            f'<img src="{user.avatar.url}" '
            f'style="max-width: 50px; max-height: 50px;" />'
        ) if user.avatar else ''

    @admin.display(description='Рецепты')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписки')
    def subscriptions_count(self, user):
        return user.authors.count()

    @admin.display(description='Подписчики')
    def subscribers_count(self, user):
        return user.followers.count()
