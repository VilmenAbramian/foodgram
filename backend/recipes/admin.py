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
        # Динамическое определение порогов N и M
        all_recipes = model_admin.model.objects.all()
        thresholds = self.get_thresholds(all_recipes)
        minimum_time, medium_time = (
            thresholds['minimum_time'],
            thresholds['medium_time']
        )

        ranges = [
            ('fast', f'быстрее {minimum_time} мин',
             {'cooking_time__lt': minimum_time}),
            ('medium', f'от {minimum_time} до {medium_time} мин', {
                'cooking_time__gte': minimum_time,
                'cooking_time__lt': medium_time}),
            ('long', f'дольше {medium_time} мин',
             {'cooking_time__gte': medium_time}),
        ]

        return [
            (key, f'{label} ({all_recipes.filter(**query).count()})')
            for key, label, query in ranges
        ]

    def queryset(self, request, queryset):
        value = self.value()
        thresholds = self.get_thresholds(queryset)

        filters = {
            'fast': {'cooking_time__lt': thresholds['minimum_time']},
            'medium': {
                'cooking_time__gte': thresholds['minimum_time'],
                'cooking_time__lt': thresholds['medium_time']
            },
            'long': {'cooking_time__gte': thresholds['medium_time']}
        }
        return queryset.filter(**filters.get(value, {}))

    def get_thresholds(self, queryset):
        cooking_times = queryset.values_list('cooking_time', flat=True)
        if cooking_times:
            min_time, max_time = min(cooking_times), max(cooking_times)
            minimum_time = min_time + (max_time - min_time) // 3
            medium_time = minimum_time + (max_time - min_time) // 3
        else:
            minimum_time, medium_time = 10, 30
        return {'minimum_time': minimum_time, 'medium_time': medium_time}


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
        ingredients = recipe.recipe_ingredients.select_related('ingredient')
        return mark_safe('<br>'.join(
            f'{item.ingredient.name} '
            f'({item.ingredient.measurement_unit}) - {item.amount}'
            for item in ingredients
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
    def in_favorites(self, recipes):
        return recipes.favoriterecipes_related.count()


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


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
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
        if user.avatar:
            return mark_safe(
                f'<img src="{user.avatar.url}" '
                f'style="max-width: 50px; max-height: 50px;" />'
            )
        return "Нет аватара"

    @admin.display(description='Количество рецептов')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Количество подписок')
    def subscriptions_count(self, user):
        return user.authors.count()

    @admin.display(description='Количество подписчиков')
    def subscribers_count(self, user):
        return user.followers.count()
