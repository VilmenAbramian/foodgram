# Generated by Django 5.1.1 on 2024-12-09 14:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_remove_user_role_alter_subscriptions_author_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(regex='^[\\w.@+-]+\\Z')], verbose_name='Имя пользователя'),
        ),
    ]
