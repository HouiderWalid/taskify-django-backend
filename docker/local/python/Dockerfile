FROM python:3.12-slim

RUN apt update && apt install -y nginx && rm -rf /var/lib/apt/lists/*

COPY docker/local/nginx/conf.d /etc/nginx/conf.d

WORKDIR /var/www/html

RUN pip install --no-cache-dir pipenv cryptography

COPY . .

RUN pipenv install --deploy --system

EXPOSE 8000

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000 & nginx -g 'daemon off;'"]