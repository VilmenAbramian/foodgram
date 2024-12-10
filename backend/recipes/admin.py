from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import FavoriteRecipes, Ingredient, Recipe, ShoppingList, Tag
from recipes.models import Subscriptions, User


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cooking_time', 'author',
        'get_tags', 'get_ingredients', 'get_image',
        'in_favorites'
    )
    list_filter = ('tags', 'author')

    def get_tags(self, recipe):
        return ', '.join([tag.name for tag in recipe.tags.all()])
    get_tags.short_description = 'Теги'

    def get_ingredients(self, recipe):
        return ', '.join(
            f'{ingredient.name} ({ingredient.measurement_unit})'
            for ingredient in recipe.ingredients.all()
        )
    get_ingredients.short_description = 'Ингредиенты'

    def get_image(self, recipe):
        if recipe.image:
            return mark_safe(
                f'<img src="{recipe.image.url}"'
                f'style="max-width: 200px; max-height: 200px;" />'
            )
    get_image.short_description = 'Картинка'

    def in_favorites(self, recipes):
        return recipes.favoriterecipes_related.count()
    in_favorites.short_description = 'В избранном'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    search_fields = ('name', 'slug',)


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'recipe__name',)
    list_filter = ('author', 'recipe',)


class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'recipe',)
    list_filter = ('author', 'recipe',)


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    list_filter = ('user', 'author',)


admin.site.register(FavoriteRecipes, FavoriteRecipesAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(User)
