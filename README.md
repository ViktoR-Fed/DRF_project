# DRF Project - API для онлайн-обучения

## Описание проекта

REST API для платформы онлайн-обучения с интеграцией Stripe, Celery и Docker.

## Требования

- Docker и Docker Compose
- Python 3.12+
- Stripe аккаунт (для тестов)

## Переменные окружения

### Обязательные Secrets (GitHub Actions)

| Secret | Описание |
|--------|----------|
| `SERVER_HOST` | IP-адрес сервера |
| `SERVER_USER` | Имя пользователя SSH |
| `SSH_PRIVATE_KEY` | Приватный SSH-ключ |
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub password |

### Настройки Django

| Переменная | Описание | Значение по умолчанию |
|------------|----------|---------------------|
| `SECRET_KEY` | Секретный ключ Django | Обязательно |
| `DEBUG` | Режим отладки | True |
| `ALLOWED_HOSTS` | Разрешенные хосты | localhost |

### База данных (PostgreSQL)

| Переменная          | Описание | Значение по умолчанию |
|---------------------|----------|---------------------|
| `NAME`              | Имя БД | drf_db |
| `USER`     | Пользователь | drf_user |
| `PASSWORD` | Пароль | Обязательно |
| `HOST`     | Хост | db |

### Redis

| Переменная | Описание | Значение по умолчанию |
|------------|----------|---------------------|
| `REDIS_HOST` | Хост | redis |
| `REDIS_PORT` | Порт | 6379 |
| `REDIS_PASSWORD` | Пароль | - |
| `REDIS_DB` | Номер БД | 0 |

### Celery

| Переменная | Описание |
|------------|----------|
| `CELERY_BROKER_URL` | URL брокера |
| `CELERY_RESULT_BACKEND` | URL для результатов |

### Stripe

| Переменная | Описание |
|------------|----------|
| `STRIPE_SECRET_KEY` | Секретный ключ |
| `STRIPE_PUBLISHABLE_KEY` | Публичный ключ |


### Email (для уведомлений)

| Переменная | Описание |
|------------|----------|
| `EMAIL_HOST` | SMTP хост |
| `EMAIL_PORT` | SMTP порт |
| `EMAIL_HOST_USER` | Логин |
| `EMAIL_HOST_PASSWORD` | Пароль |
| `DEFAULT_FROM_EMAIL` | Отправитель |

## Настройка окружения

### 1. Создание .env файла

```bash
cp .env.template .env
# Заполните значения