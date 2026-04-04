# Weather Alert Service

Сервис для автоматического отслеживания погоды и отправки уведомлений при изменении температуры. Подходит для оповещения о резких перепадах погоды, заморозках или потеплении.

## Возможности

- 🌤️ **Ежечасная проверка погоды** (Celery Beat)
- 📧 **Email-уведомления** при изменении температуры более чем на 1°C
- 👤 **Регистрация и JWT-аутентификация**
- 📍 **Подписка на погоду в любом городе**
- 🐳 **Полная контейнеризация** (Docker + docker-compose)
- 📚 **Автоматическая документация API** (Swagger)

## Технологии

| Компонент | Технология |
|-----------|------------|
| Backend | FastAPI, Python 3.10 |
| Database | PostgreSQL, SQLAlchemy |
| Queue | Celery, Redis |
| Auth | JWT, bcrypt |
| Container | Docker, docker-compose |
| HTTP client | httpx, requests |

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

OPENWEATHER_API_KEY — получите бесплатно на openweathermap.org

SMTP_USER и SMTP_PASSWORD — для email-уведомлений (можно использовать Gmail)

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
## Автор
UZer88 — GitHub

## Лицензия
MIT