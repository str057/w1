from django.core.management.base import BaseCommand
import telegram
from django.conf import settings
import json


def get_bot_instance():
    """Get bot instance directly"""
    return telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)


class Command(BaseCommand):
    help = "Setup Telegram bot webhook"

    def add_arguments(self, parser):
        parser.add_argument(
            "--set-webhook", action="store_true", help="Set webhook URL"
        )
        parser.add_argument(
            "--get-webhook", action="store_true", help="Get webhook info"
        )
        parser.add_argument(
            "--delete-webhook", action="store_true", help="Delete webhook"
        )
        parser.add_argument("--status", action="store_true", help="Get bot status")

    def handle(self, *args, **options):
        bot = get_bot_instance()

        if options["status"]:
            self.get_bot_status(bot)
        elif options["get_webhook"]:
            self.get_webhook_info(bot)
        elif options["delete_webhook"]:
            self.delete_webhook(bot)
        elif options["set_webhook"]:
            self.set_webhook(bot)
        else:
            self.get_bot_status(bot)

    def get_bot_status(self, bot):
        try:
            bot_info = bot.get_me()
            self.stdout.write(
                self.style.SUCCESS(f"Bot: {bot_info.first_name} (@{bot_info.username})")
            )
            self.stdout.write(f"Bot ID: {bot_info.id}")

            # Get webhook info
            webhook_info = bot.get_webhook_info()
            self.stdout.write(f"Webhook URL: {webhook_info.url}")
            self.stdout.write(f"Webhook set: {webhook_info.url is not None}")

            if webhook_info.pending_update_count:
                self.stdout.write(
                    f"Pending updates: {webhook_info.pending_update_count}"
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

    def get_webhook_info(self, bot):
        try:
            webhook_info = bot.get_webhook_info()
            self.stdout.write(json.dumps(webhook_info.to_dict(), indent=2))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

    def delete_webhook(self, bot):
        try:
            bot.delete_webhook()
            self.stdout.write(self.style.SUCCESS("Webhook deleted"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

    def set_webhook(self, bot):
        try:
            # Замените на ваш реальный URL
            webhook_url = "https://your-domain.com/telegram/webhook/"
            bot.set_webhook(webhook_url)
            self.stdout.write(self.style.SUCCESS(f"Webhook set to: {webhook_url}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
