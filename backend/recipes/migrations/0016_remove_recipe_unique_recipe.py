# Generated by Django 5.1.1 on 2024-12-02 18:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0015_alter_favoriterecipes_options_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipe',
            name='unique_recipe',
        ),
    ]
