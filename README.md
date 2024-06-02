# groceries project

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Разворачивание
В папке infra 
docker-compose up --build
после python manage.py makemigrations
python manage.py migrate
в контейнерах infra-backend и infra-web

Python 3.7
Django 3.2

Стэк: python, Docker, Django, gunicorn
