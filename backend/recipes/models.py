from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


# ---- Модели для пользователя ----
class User(AbstractUser):
    '''
    Кастомная модель пользователя
    '''
    USER = 'user'
    ADMIN = 'admin'
    ROLE_USER = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор')
    ]
    username = models.CharField(max_length=128, unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=16, choices=ROLE_USER,
                            default=USER)
    avatar = models.ImageField(
        upload_to='users/images/',
        null=True,
        default=None
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followed'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribe'
            )
        ]

# ---- Модели для рецептов ----
class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента')
    measurement_unit = models.CharField(
        max_length=128,
        verbose_name='Единица измерения',
        help_text='Введите название единицы измерения')

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='Название тега',
        help_text='Введите название тега'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг тега',
        help_text='Введите слаг тега'
    )
    color = models.CharField(
        max_length=64,
        verbose_name='Цвет тега',
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
    image = models.ImageField(
        upload_to='media/',
        verbose_name='Изображение рецепта',
        help_text='Добавьте изображение рецепта'
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1.0)],
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления рецепта в минутах'

    )

    class Meta:
        ordering = ['-id']
        default_related_name = 'recipe'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    # def __str__(self):
    #     return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',
        help_text='Выберите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        help_text='Укажите ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'Минимальное количество ингредиентов 1')],
        verbose_name='Количество',
        help_text='Укажите количество ингредиента'
    )

    class Meta:
        verbose_name = 'Cостав рецепта'
        verbose_name_plural = 'Состав рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients')
        ]

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

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_cart'
            )
        ]


class FavoriteRecipes(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_favorite'
            )
        ]
