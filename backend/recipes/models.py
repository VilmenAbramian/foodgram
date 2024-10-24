from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    unit = models.CharField(max_length=8)


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=64)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=256)
    image = models.ImageField(upload_to='media/')
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tag = models.ManyToManyField(Tag)
    time = models.IntegerField()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField()


class ShoppingList(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class FavoriteRecipes(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite',)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorite',)
