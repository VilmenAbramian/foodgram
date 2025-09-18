
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

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-Django%20REST%20Framework-red?style=for-the-badge)

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)![Gunicorn](https://img.shields.io/badge/Gunicorn-499C57?style=for-the-badge)![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)

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
python manage.py import_tags
python manage.py import_ingredients
```

## 📑 API и документация
```
http://<ваш-хост>/api/docs
```

## 👤 Автор
[Вильмен Абрамян](https://github.com/VilmenAbramian), vilmen.abramian@gmail.com
