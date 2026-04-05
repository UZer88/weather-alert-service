import httpx
import logging
from app.config import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)


async def send_telegram_alert(chat_id: str, city: str, old_temp: float, new_temp: float, condition: str):
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not configured, skipping notification")
        return

    message = (
        f"🌍 *{city}*\n"
        f"🌡️ Температура изменилась: {old_temp}°C → {new_temp}°C\n"
        f"☁️ {condition}\n"
        f"📅 {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Telegram notification sent to {chat_id}")
    except Exception as e:
        logger.error(f"❌ Failed to send Telegram notification: {e}")