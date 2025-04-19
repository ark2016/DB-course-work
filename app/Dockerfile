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
