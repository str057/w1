import os
from django.conf import settings

try:
    from telegram import Bot
    from telegram.constants import ParseMode
except ImportError:
    print(
        "Warning: python-telegram-bot not installed. "
        "Install with: pip install python-telegram-bot"
    )

    # Заглушка для тестирования
    class Bot:
        def __init__(self, token):
            self.token = token

        def get_me(self):
            return type(
                "obj",
                (object,),
                {"first_name": "Test Bot", "username": "test_bot", "id": 123456},
            )()

        def get_updates(self, offset=None, timeout=30):
            return []

        def send_message(self, chat_id, text, parse_mode=None):
            print(f"DEBUG: Would send to {chat_id}: {text}")
            return type("obj", (object,), {"message_id": 1})()

        def get_webhook_info(self):
            return type(
                "obj",
                (object,),
                {
                    "url": None,
                    "has_custom_certificate": False,
                    "pending_update_count": 0,
                },
            )()

        def set_webhook(self, url):
            print(f"DEBUG: Would set webhook to {url}")
            return True

        def delete_webhook(self):
            print("DEBUG: Would delete webhook")
            return True


def get_bot_instance():
    """Get Telegram bot instance"""
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    if not token:
        # Попробуем получить из переменных окружения
        token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN not set in settings or environment variables"
        )

    return Bot(token=token)


def send_telegram_message(chat_id, message):
    """Send message to Telegram"""
    bot = get_bot_instance()
    return bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
