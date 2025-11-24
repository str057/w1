from django.apps import AppConfig


class TelegramBotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "telegram_bot"

    def ready(self):
        # Убираем проблемный импорт или комментируем его
        # import telegram.signals  # Удалите или закомментируйте эту строку
        pass
