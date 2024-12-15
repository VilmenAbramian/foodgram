from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


AMOUNT_MIN_VALUE = 1
MIN_COOCKING_TIME = 1


# ---- Модели для пользователя ----
class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=(RegexValidator(regex=r'^[\w.@+-]+\Z'),),
    )
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(unique=True, max_length=254)
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        default=None
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('first_name',)


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='followers', verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='authors', verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            )
        ]


# ---- Модели для рецептов ----
class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='Название',
        help_text='Введите название')
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Ед. измерения',
        help_text='Введите название ед. измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Название',
        help_text='Введите название'
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        verbose_name='Слаг',
        help_text='Введите слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='media/',
        verbose_name='Изображение рецепта',
        help_text='Добавьте изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(MIN_COOCKING_TIME)],
        verbose_name='Время приготовления (мин)',
        help_text='Укажите время приготовления рецепта в минутах'

    )

    class Meta:
        ordering = ('name', 'cooking_time',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,

        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
        help_text='Укажите ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                AMOUNT_MIN_VALUE,
                f'Минимальное количество ингредиентов {AMOUNT_MIN_VALUE}'
            ),
        ),
        verbose_name='Мера',
        help_text='Укажите количество ингредиента'
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredients'),
        )

    def __str__(self):
        return (f'{self.ingredient} {self.amount} '
                f'{self.ingredient.measurement_unit}')


class UserRecipeRelation(models.Model):
    author = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='%(class)s'
    )
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, related_name='%(class)s'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_%(class)s'
            )
        ]


class ShoppingList(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списоки покупок'


class FavoriteRecipes(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
