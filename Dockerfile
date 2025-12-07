# 1. Беремо за основу легкий Linux з Python 3.11
FROM python:3.11-slim

# 2. Вимикаємо зайві кеші пітона (щоб працювало швидше)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Створюємо робочу папку всередині контейнера
WORKDIR /code

# 4. Копіюємо файл з бібліотеками
COPY requirements.txt /code/

# 5. Встановлюємо бібліотеки
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копіюємо весь наш код (папку app) всередину
COPY ./app /code/app

# 7. Цей порт буде доступний (просто для інформації)
EXPOSE 8000