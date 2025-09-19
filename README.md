# 🍲 Foodgram — твой кулинарный помощник!  
  
![example workflow](https://github.com/VilmenAbramian/foodgram/actions/workflows/main.yml/badge.svg)  
Веб-сервис, где пользователи публикуют рецепты, сохраняют понравившиеся, подписываются на любимых авторов и формируют удобные списки покупок прямо перед походом в магазин.  
  
<img width="2000" height="2424" alt="foodgram" src="https://github.com/user-attachments/assets/70879d94-584a-4e23-9d78-aefaded169e1" />  
  
  
## ✨ Основные возможности  
- 📝 **Публикация рецептов** — добавляй пошаговые инструкции и аппетитные фото.  
- ⭐ **Избранное** — сохраняй лучшие рецепты, чтобы они всегда были под рукой.  
- 👨‍🍳 **Подписки** — следи за новыми публикациями любимых авторов.  
- 🛒 **Списки покупок** — автоматически формируй список ингредиентов для выбранных блюд.  
  
## 🛠 Технологии  
  
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)  
![DRF](https://img.shields.io/badge/DRF-Django%20REST%20Framework-red?style=for-the-badge)  
  
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499C57?style=for-the-badge)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)  
  
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)  
![CI/CD](https://img.shields.io/badge/CI--CD-автоматизация-blue?style=for-the-badge)  
  
## 🚀 Быстрый старт (Docker)  
  
Запусти Foodgram локально в пару команд:  
```bash  
git clone https://github.com/VilmenAbramian/foodgram.git
cd foodgram
docker compose up -d
```  
Далее в контейнере **backend**:  
```bash  
python manage.py migrate  
python manage.py collectstatic --no-input  
cp -r /app/collected_static/. /backend_static/static/  
python manage.py import_tags # Импорт фикстур с тегами для рецептов
python manage.py import_ingredients # Импорт фикстур с ингредиентами для рецептов
python manage.py createsuperuser # Создать пользователя с правами администратора
```
Чтобы вводить команды прямо из терминала (не заходя во вкладку `exec` соответствующего контейнера в графическом интерфейсе программы Docker Dashboard) перед каждой из них нужно добавить: 
```bash
sudo docker compose -f docker-compose.production.yml exec
```
После загрузки проекта на сервер нужно добавить в директорию проекта файл `.env` и заполнить его реальными данными (пример находится в файле `.env.example`

## 🌐 Настройка внешнего NGINX

Далее нужно настроить параметры внешнего nginx. Ниже приведён пример конфигурационного файла в случае размещения на сервере двух проектов:
```
## Kittygram project
server {
    server_name kittygram.pro www.kittygram.pro;
    client_max_body_size 20m;

    location / {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /media/ {
        proxy_pass http://127.0.0.1:9000/media/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        proxy_pass http://127.0.0.1:9000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/kittygram.pro/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/kittygram.pro/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot 
}

server {
    if ($host = www.kittygram.pro) {
    return 301 https://$host$request_uri;
    } # managed by Certbot

    if ($host = kittygram.pro) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name kittygram.pro www.kittygram.pro;
    return 404; # managed by Certbot
}

## Foodgram project
server {
    server_name foodgram.info www.foodgram.info;
    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:7080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/foodgram/foodgram.info.crt;
    ssl_certificate_key /etc/nginx/ssl/foodgram/foodgram.info.key;
    ssl_trusted_certificate /etc/nginx/ssl/foodgram/foodgram.info.ca_bundle;
}

server {
    listen 80;
    server_name foodgram.info www.foodgram.info;
    return 301 https://$host$request_uri;
}
```
  
## 📑 Дополнительно
Интерактивная документация сервиса доступна по адресу:
```  
http://<ваш-хост>/api/docs  
```
Админка доступна по адресу:
```  
http://<ваш-хост>/admin 
```
  
## 👤 Автор  
[Вильмен Абрамян](https://github.com/VilmenAbramian), vilmen.abramian@gmail.com