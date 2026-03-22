import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD


def send_weather_alert(email: str, city: str, old_temp: float, new_temp: float, condition: str):
    subject = f"🌦️ Погода в {city} изменилась"

    body = f"""
    Привет!

    Погода в {city} изменилась:

    🌡️ Температура: {old_temp}°C → {new_temp}°C
    ☁️ Условия: {condition}

    Будь осторожен и одевайся по погоде!

    ---
    Weather Alert Service
    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"✅ Уведомление отправлено на {email}")
    except Exception as e:
        print(f"❌ Ошибка отправки email: {e}")