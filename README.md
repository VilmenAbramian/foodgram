# Foodgram
Автор: [[9882016alpha@gmail.com | Абрамян Вильмен Левонович]]
Используемый стек:
`Python` `Django` `Django Rest Framework` `Docker` `Gunicorn` `NGINX` `PostgreSQL` `Yandex Cloud` `Continuous Integration` `Continuous Deployment`

Онлайн-сервис для публикации рецептов. На этом сервисе пользователи публикуют свои рецепты, подписываются на публикации других пользователей, добавляют понравившиеся рецепты в избранное, а перед походом в магазин могут скачать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Команды для локального запуска через Docker:
```
git clone https://github.com/VilmenAbramian/foodgram
docker compose up
```
Далее внутри контейнера backend выполнить команды:
```
python manage.py migrate
python manage.py collectstatic
cp -r /app/collected_static/. /backend_static/static/
python manage.py import_tags
python manage.py import_ingredients
```
Для запуска API проекта после клонирования репозитория выполнить команды:
```
pip install -r requirements.txt
Далее по списку выше
```
Документация сервиса доступна по ссылке:
```
[[http://foodgram_url/api/docs | Документация API]]
```