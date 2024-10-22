from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer, CreateUserSerializer

class MyPagePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = MyPagePagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    @action(detail=False,
            methods=['get', 'post'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        '''Получить свой профиль'''
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        '''Изменить пароль'''
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request':request}
        )
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
            return Response('Пароль успешно изменён', status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        user = self.request.user
        if request.method == 'DELETE':
            return Response('Изображение профиля успешно удалено', status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_avatar = serializer.validated_data.get('avatar')
        user.avatar = new_avatar
        user.save()
        if new_avatar is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        image_url = request.build_absolute_uri(
            request.user.avatar.url
        )
        return Response({'avatar': str(image_url)}, status=status.HTTP_200_OK)
