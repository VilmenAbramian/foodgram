# Generated by Django 5.1.1 on 2024-12-13 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_alter_user_first_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=150),
        ),
    ]
