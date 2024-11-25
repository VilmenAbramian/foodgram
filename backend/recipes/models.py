from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name = 'Название ингредиента',
        help_text='Введите название ингредиента')
    measurement_unit = models.CharField(
        max_length=8,
        verbose_name='Единица измерения',
        help_text='Введите название единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name = 'Название тега',
        help_text='Введите название тега'
        )
    slug = models.SlugField(
        unique=True,
        verbose_name = 'Слаг тега',
        help_text='Введите слаг тега'
        )
    color = models.CharField(
        max_length=64,
        verbose_name = 'Цвет тега',
        help_text='Введите значение цвета тега'
        )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='media/')
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1.0)]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class ShoppingList(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list'
    )


class FavoriteRecipes(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite',)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorite',)
