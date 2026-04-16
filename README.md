# Weather Alert Service

[![CI](https://github.com/UZer88/weather-alert-service/actions/workflows/ci.yml/badge.svg)](https://github.com/UZer88/weather-alert-service/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-76%25-brightgreen)](https://github.com/UZer88/weather-alert-service)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Сервис для автоматического отслеживания погоды и отправки уведомлений при изменении температуры. Подходит для оповещения о резких перепадах погоды, заморозках или потеплении.

## Возможности

- 🌤️ **Ежечасная проверка погоды** (Celery Beat)
- 📧 **Email-уведомления** при изменении температуры более чем на 1°C
- 📱 **Telegram-уведомления** (опционально)
- 👤 **Регистрация и JWT-аутентификация**
- 📍 **Подписка на погоду в любом городе**
- 🐳 **Полная контейнеризация** (Docker + docker-compose)
- 📚 **Автоматическая документация API** (Swagger)
- ✅ **Тесты** (pytest, покрытие 76%)
- 🔧 **Линтер и форматтер** (ruff)

## Технологии

| Компонент | Технология |
|-----------|------------|
| Backend | FastAPI, Python 3.12 |
| Database | PostgreSQL, SQLAlchemy |
| Queue | Celery, Redis |
| Auth | JWT, bcrypt |
| Container | Docker, docker-compose |
| HTTP client | httpx, requests |
| Testing | pytest, pytest-asyncio, pytest-cov |
| Linter | ruff |

## Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/UZer88/weather-alert-service
cd weather-alert-service
```

### 2. Настройте переменные окружения
```bash
cp .env.example .env
# Отредактируйте .env — добавьте API ключи
```

### Минимальная конфигурация для работы:

- OPENWEATHER_API_KEY — получите бесплатно на openweathermap.org

- SMTP_USER и SMTP_PASSWORD — для email-уведомлений (можно использовать Gmail)

### 3. Запустите сервис
```bash
docker-compose up -d
```

### 4. Откройте в браузере
- Swagger документация: http://localhost:8001/docs
- Проверка здоровья: http://localhost:8001/ping

## Как это работает

1. Пользователь регистрируется и получает JWT токен

2. Создаёт подписку на город (например, Moscow)

3. Celery Beat каждый час запускает задачу check_all_weather

4. Задача проверяет погоду для всех активных подписок

5. Если температура изменилась на ≥1°C — отправляется email

## Запуск тестов
```bash
# Установка зависимостей для тестов
pip install -r requirements.txt

# Запуск всех тестов
pytest tests/test_api.py -v

# Запуск с покрытием
pytest tests/test_api.py --cov=app --cov-report=term
```

## Мониторинг и логи
```bash
# Посмотреть логи всех сервисов
docker-compose logs -f

# Только Celery worker
docker-compose logs -f celery_worker

# Только API
docker-compose logs -f app

# Запустить задачу вручную
docker-compose exec celery_worker celery -A celery_app call celery_tasks.check_all_weather
```

## Остановка сервиса
```bash
docker-compose down
```

## CI/CD
Проект использует GitHub Actions для:
- Автоматического запуска тестов (12 тестов)
- Проверки покрытия кода (минимальный порог 70%)
- Линтинга с ruff

## Автор
UZer88

## Лицензия
MIT