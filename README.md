# DRF Project - API для онлайн-обучения

## Описание проекта

Проект представляет собой REST API для платформы онлайн-обучения с функционалом:
- Управление курсами и уроками
- Аутентификация через JWT
- Подписка на обновления курсов
- Интеграция с Stripe для оплаты
- Celery для фоновых задач и уведомлений
- Docker для контейнеризации

## Требования

- Docker и Docker Compose
- Python 3.12+ (для локальной разработки)


## Деплой на сервер

### Требования
- Docker и Docker Compose на сервере
- Настроенные GitHub Secrets

### Автоматический деплой
При пуше в ветку `main` или `master`:
1. Запускаются тесты
2. Собирается Docker-образ
3. Образ загружается в Docker Hub
4. Происходит деплой на сервер

### Ручной деплой

```bash
# Сборка образа
docker build -f Dockerfile.prod -t drf-project:latest .

# Загрузка на сервер
scp -r . deploy@your-server-ip:/app/drf_project

# На сервере
cd /app/drf_project
docker-compose up -d --build