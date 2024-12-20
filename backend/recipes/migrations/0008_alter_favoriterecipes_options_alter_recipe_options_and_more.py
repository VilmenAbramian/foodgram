# Generated by Django 5.1.1 on 2024-12-13 10:06

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_alter_favoriterecipes_author_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favoriterecipes',
            options={'verbose_name': 'Избранный рецепт', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_related_name': 'recipes', 'ordering': ('name', 'cooking_time'), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={},
        ),
        migrations.AlterModelOptions(
            name='shoppinglist',
            options={'verbose_name': 'Список покупок', 'verbose_name_plural': 'Списоки покупок'},
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(help_text='Введите название ед. измерения', max_length=64, verbose_name='Ед. измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(help_text='Введите название', max_length=128, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(help_text='Укажите время приготовления рецепта в минутах', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время приготовления (мин)'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(help_text='Укажите ингредиенты', on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.ingredient'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(help_text='Выберите рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authors', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(help_text='Введите слаг', max_length=32, unique=True, verbose_name='Слаг'),
        ),
    ]
