
# 🍲 Foodgram — your culinary assistant!
A web service where users can publish recipes, save their favorites, follow authors they like, and generate handy shopping lists right before heading to the store.

<img width="2000" height="2424" alt="foodgram" src="https://github.com/user-attachments/assets/70879d94-584a-4e23-9d78-aefaded169e1" />

## ✨ Key Features
- 📝 **Publish recipes** — add step-by-step instructions and appetizing photos.  
- ⭐ **Favorites** — save the best recipes to always have them at hand.  
- 👨‍🍳 **Subscriptions** — follow your favorite authors and stay updated.  
- 🛒 **Shopping lists** — automatically generate ingredient lists for selected dishes.  

## 🛠 Technologies

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-Django%20REST%20Framework-red?style=for-the-badge)

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)![Gunicorn](https://img.shields.io/badge/Gunicorn-499C57?style=for-the-badge)![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI--CD-automation-blue?style=for-the-badge)

---

## 🚀 Quick Start (Docker)

Run Foodgram locally in just a few commands:
```bash
git clone https://github.com/VilmenAbramian/foodgram.git
cd foodgram
docker compose up -d
```

Then inside the **backend** container:
```bash
python manage.py migrate
python manage.py collectstatic --no-input
cp -r /app/collected_static/. /backend_static/static/
python manage.py import_tags
python manage.py import_ingredients
```

## 📑 API and Documentation
```
http://<your-host>/api/docs
```

## 👤 Author
[Vilmen Abramian](https://github.com/VilmenAbramian), vilmen.abramian@gmail.com
