from django.contrib import admin

from .models import FavoriteRecipes, Ingredient, Recipe, ShoppingList, Tag
from users.models import Subscriptions


admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(ShoppingList)
admin.site.register(Tag)

admin.site.register(Subscriptions)
admin.site.register(FavoriteRecipes)
