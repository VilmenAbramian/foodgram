from rest_framework import viewsets
from rest_framework.decorators import action

from users.models import User
from users.serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True)
    def me(self, request):
        '''Получить свой профиль'''
        ...

    @action(detail=True)
    def set_password(self, request, *args, **kwargs):
        '''Изменить пароль'''
        ...

    @action(detail=True)
    def subscribe(self, request, *args, **kwargs):
        '''Создать и/или удалить подписку'''
        ...

    @action(detail=False)
    def subscriptions(self, request):
        '''Отобразить все подписки пользователя'''
        ...

    @action(detail=True)
    def avatar(self, reuest):
        '''Добавить или изменить аватар пользователя'''