# Generated by Django 5.1.1 on 2024-10-18 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default=None, null=True, upload_to='users/images/'),
        ),
    ]
