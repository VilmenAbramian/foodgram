from django.contrib.auth.models import AbstractUser
from django.db import models


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
    REQUIRED_FIELDS = ['username','password','first_name','last_name']


class Subscriptions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower',)
    author = models.ForeignKey(User,  on_delete=models.CASCADE, related_name='followed',)