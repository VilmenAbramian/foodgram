# 🍲 Foodgram — your cooking assistant!  
  
![example workflow](https://github.com/VilmenAbramian/foodgram/actions/workflows/main.yml/badge.svg)  
A web service where users can publish recipes, save their favorites, follow their favorite authors, and generate convenient shopping lists right before going to the store.  
  
<img width="2000" height="2424" alt="foodgram" src="https://github.com/user-attachments/assets/70879d94-584a-4e23-9d78-aefaded169e1" />  
  
  
## ✨ Key Features  
- 📝 **Recipe Publishing** — add step-by-step instructions and appetizing photos.  
- ⭐ **Favorites** — save the best recipes to always have them at hand.  
- 👨‍🍳 **Subscriptions** — keep track of new posts from your favorite authors.  
- 🛒 **Shopping Lists** — automatically generate a list of ingredients for selected dishes.  
  
## 🛠 Technologies  
  
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)  
![DRF](https://img.shields.io/badge/DRF-Django%20REST%20Framework-red?style=for-the-badge)  
  
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499C57?style=for-the-badge)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)  
  
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)  
![CI/CD](https://img.shields.io/badge/CI--CD-automation-blue?style=for-the-badge)  
  
## 🚀 Quick Start (Docker)  
  
Run Foodgram locally in a couple of commands:  
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
python manage.py import_tags # Import fixtures with tags for recipes
python manage.py import_ingredients # Import fixtures with ingredients for recipes
python manage.py createsuperuser # Create an administrator account
```
To run commands directly from the terminal (without going into the `exec` tab of the Docker Dashboard container), prepend each of them with: 
```bash
sudo docker compose -f docker-compose.production.yml exec
```
After deploying the project on the server, add a `.env` file to the project directory and fill it with real data (an example is provided in `.env.example`).

## 🌐 External NGINX Configuration

Next, you need to configure the external nginx parameters. Below is an example of the configuration file when hosting two projects on one server:
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
  
## 📑 Additional Info
Interactive API documentation is available at:
```  
http://<your-host>/api/docs  
```
Admin panel is available at:
```  
http://<your-host>/admin 
```
  
## 👤 Author  
[Vilmen Abramian](https://github.com/VilmenAbramian), vilmen.abramian@gmail.com
