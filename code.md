### docker-compose.yml

```

services:
  db:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_DB: fox_survey
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build:
      context: ./app
      dockerfile: Dockerfile
    command: >
      bash -c "python manage.py migrate --noinput &&
               python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ./app:/app
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    environment:
      DJANGO_SECRET_KEY: "replace-this-in-prod"
      DJANGO_DEBUG: "True"
      DJANGO_ALLOWED_HOSTS: "localhost,127.0.0.1"
      POSTGRES_DB: fox_survey
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_HOST: db
      POSTGRES_PORT: "5432"

volumes:
  db_data:
```

## app

#### Dockerfile

```
# app/Dockerfile
FROM python:3.11-slim

# Отключаем буферизацию вывода и pyc
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Устанавливаем системные зависимости (если нужны)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Копируем код проекта
COPY . .

# Открываем порт
EXPOSE 8000

# По умолчанию выполняем миграции и запускаем сервер
CMD ["bash", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
```

#### /manage.py

```
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foxsurvey.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Не удалось импортировать Django") from exc
    execute_from_command_line(sys.argv)

```

#### /requirements.txt

```
Django>=4.2,<5.0
psycopg2-binary>=2.9
gunicorn>=20.1

```

#### /foxsurvey/settings.py

```
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "unsafe-default")
DEBUG = os.environ.get("DJANGO_DEBUG", "") != "False"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "fox_survey"),
        "USER": os.environ.get("POSTGRES_USER", "user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "pass"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'foxsurvey.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ],},
}]

WSGI_APPLICATION = 'foxsurvey.wsgi.application'

# Остальные настройки (статика, локализация и т.д.)

```

#### /foxsurvey/urls.py

```

```

#### /foxsurvey/wsgi.py

```
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foxsurvey.settings")
application = get_wsgi_application()

```

#### /foxsurvey/__init__.py

```

```

