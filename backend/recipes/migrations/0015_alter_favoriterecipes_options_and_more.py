# Generated by Django 5.1.1 on 2024-12-02 17:06

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_alter_shoppinglist_author_alter_shoppinglist_recipe'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favoriterecipes',
            options={'verbose_name': 'Избранные рецепты', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['id'], 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_related_name': 'recipe', 'ordering': ['-id'], 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'verbose_name': 'Cостав рецепта', 'verbose_name_plural': 'Состав рецепта'},
        ),
        migrations.AlterModelOptions(
            name='shoppinglist',
            options={'verbose_name': 'Список покупок', 'verbose_name_plural': 'Список покупок'},
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(help_text='Введите название единицы измерения', max_length=128, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(help_text='Укажите время приготовления рецепта в минутах', validators=[django.core.validators.MinValueValidator(1.0)], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(help_text='Добавьте изображение рецепта', upload_to='media/', verbose_name='Изображение рецепта'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(help_text='Укажите количество ингредиента', validators=[django.core.validators.MinValueValidator(1, 'Минимальное количество ингредиентов 1')], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(help_text='Укажите ингредиенты', on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(help_text='Выберите рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipe', verbose_name='Название рецепта'),
        ),
        migrations.AddConstraint(
            model_name='favoriterecipes',
            constraint=models.UniqueConstraint(fields=('author', 'recipe'), name='unique_favorite'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(fields=('name', 'author'), name='unique_recipe'),
        ),
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_ingredients'),
        ),
        migrations.AddConstraint(
            model_name='shoppinglist',
            constraint=models.UniqueConstraint(fields=('author', 'recipe'), name='unique_cart'),
        ),
    ]
