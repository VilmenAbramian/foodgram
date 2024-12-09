from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


MIN_VALUE = 1


# ---- Модели для пользователя ----
class User(AbstractUser):
    '''
    Кастомная модель пользователя
    '''
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+\Z',
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=(username_validator,),
        verbose_name="Имя пользователя",
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, max_length=254)
    password = models.CharField(max_length=128)
    avatar = models.ImageField(
        upload_to='users/images/',
        null=True,
        default=None
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password', 'first_name', 'last_name')


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followed_users'
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
        verbose_name='Название',
        help_text='Введите название ингредиента')
    measurement_unit = models.CharField(
        max_length=128,
        verbose_name='Мера',
        help_text='Введите название меры')

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
        verbose_name='Слаг тега',
        help_text='Введите слаг тега'
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
        ordering = ('-id',)
        default_related_name = 'recipe'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
        verbose_name='Название',
        help_text='Выберите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients',
        on_delete=models.CASCADE,
        help_text='Укажите ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                MIN_VALUE, 'Минимальное количество ингредиентов 1'
            ),
        ),
        verbose_name='Мера',
        help_text='Укажите количество ингредиента'
    )

    class Meta:
        verbose_name = 'Cостав рецепта'
        verbose_name_plural = 'Составы рецептов'
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
        'User', on_delete=models.CASCADE, related_name='%(class)ss'
    )
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, related_name='%(class)ss'
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
        verbose_name_plural = 'Список покупок'


class FavoriteRecipes(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
