import os
import httpx
from celery import shared_task
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.config import DATABASE_URL, OPENWEATHER_API_KEY
from notifiers.email import send_weather_alert

sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", ""))
SessionLocal = sessionmaker(bind=sync_engine)


@shared_task
def check_all_weather():
    """Проверяет погоду для всех активных подписок"""
    db = SessionLocal()
    from app.models import Subscription
    subscriptions = db.query(Subscription).filter(Subscription.is_active == True).all()

    for sub in subscriptions:
        check_weather_for_subscription(sub.id)

    db.close()


@shared_task
def check_weather_for_subscription(subscription_id: int):
    """Проверяет погоду для одной подписки"""
    db = SessionLocal()
    from app.models import Subscription, User

    sub = db.query(Subscription).get(subscription_id)
    if not sub or not sub.is_active:
        db.close()
        return

    api_key = OPENWEATHER_API_KEY
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": sub.city,
        "appid": api_key,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = httpx.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            new_temp = data["main"]["temp"]
            condition = data["weather"][0]["description"]

            if sub.last_temp is not None:
                if abs(new_temp - sub.last_temp) >= 1.0:
                    user = db.query(User).get(sub.user_id)
                    send_weather_alert(
                        email=user.email,
                        city=sub.city,
                        old_temp=sub.last_temp,
                        new_temp=new_temp,
                        condition=condition
                    )

            sub.last_temp = new_temp
            sub.last_condition = condition
            db.commit()

    except Exception as e:
        print(f"Ошибка при получении погоды для {sub.city}: {e}")

    db.close()