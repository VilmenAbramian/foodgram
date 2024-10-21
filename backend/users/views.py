from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer

class MyPagePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = MyPagePagination

    @action(detail=False,
            methods=['get', 'post'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        '''Получить свой профиль'''
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

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

    @action(detail=True,
            methods=['get', 'post', 'put', 'delete'],
            permission_classes=[IsAuthenticated])
    def avatar(self, request, *args, **kwargs):
        '''Добавить или изменить аватар пользователя'''
        new_avatar = request.data.get('avatar')
        if new_avatar is None:
            if request.method == 'DELETE':
                return Response('Изображение профиля успешно удалено', status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user
        serializer = UserSerializer(user, data={'avatar': new_avatar})
        if serializer.is_valid():
            serializer.save()
        if request.method == 'PUT':
            return Response(serializer.data)
        