import os
import logging
import sys
import requests
from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL, OPENWEATHER_API_KEY
from notifiers.email import send_weather_alert

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)

logger = logging.getLogger(__name__)

# Создаём синхронный движок для Celery (заменяем asyncpg на psycopg2)
SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")
engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@shared_task
def check_all_weather():
    """Проверяет погоду для всех активных подписок"""
    logger.info("Запуск проверки погоды для всех подписок")
    db = SessionLocal()
    from app.models import Subscription

    try:
        subscriptions = db.query(Subscription).filter(Subscription.is_active == True).all()
        logger.info(f"Найдено активных подписок: {len(subscriptions)}")

        for sub in subscriptions:
            check_weather_for_subscription.delay(sub.id)

    except Exception as e:
        logger.error(f"Ошибка при получении списка подписок: {e}", exc_info=True)
    finally:
        db.close()
        logger.debug("Соединение с БД закрыто")


@shared_task
def check_weather_for_subscription(subscription_id: int):
    """Проверяет погоду для одной подписки"""
    logger.debug(f"Начало проверки подписки #{subscription_id}")
    db = SessionLocal()
    from app.models import Subscription, User

    try:
        sub = db.query(Subscription).get(subscription_id)
        if not sub:
            logger.warning(f"Подписка #{subscription_id} не найдена")
            return

        if not sub.is_active:
            logger.debug(f"Подписка #{subscription_id} неактивна, пропускаем")
            return

        if not OPENWEATHER_API_KEY:
            logger.error("OPENWEATHER_API_KEY не установлен")
            return

        logger.info(f"Запрос погоды для города: {sub.city}")

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": sub.city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "ru"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        new_temp = data.get("main", {}).get("temp")
        condition = data.get("weather", [{}])[0].get("description", "unknown")

        if new_temp is None:
            logger.warning(f"Не удалось получить температуру для {sub.city}")
            return

        logger.info(f"Текущая погода в {sub.city}: {new_temp}°C, {condition}")

        if sub.last_temp is not None:
            temp_diff = abs(new_temp - sub.last_temp)
            if temp_diff >= 1.0:
                user = db.query(User).get(sub.user_id)
                if user and user.email:
                    send_weather_alert(
                        email=user.email,
                        city=sub.city,
                        old_temp=sub.last_temp,
                        new_temp=new_temp,
                        condition=condition
                    )
                    logger.info(f"✅ Уведомление отправлено для {sub.city}: {sub.last_temp}°C → {new_temp}°C")
        else:
            logger.info(f"Первое обновление погоды для {sub.city}")

        sub.last_temp = new_temp
        sub.last_condition = condition
        db.commit()
        logger.debug(f"Погода обновлена для {sub.city}")

    except requests.Timeout:
        logger.error(f"⏱️ Таймаут при запросе погоды для {sub.city}")
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else "unknown"
        logger.error(f"🌐 HTTP {status} ошибка для {sub.city}: {e}")
    except requests.RequestException as e:
        logger.error(f"📡 Сетевая ошибка для {sub.city}: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"💥 Ошибка для подписки #{subscription_id}: {e}", exc_info=True)
    finally:
        db.close()
        logger.debug(f"Соединение закрыто для подписки #{subscription_id}")