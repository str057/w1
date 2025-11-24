from django.core.management.base import BaseCommand
from telegram import Bot
from django.conf import settings
import asyncio


class Command(BaseCommand):
    help = "Test Telegram bot connection"

    def handle(self, *args, **options):
        # Запускаем асинхронную функцию
        asyncio.run(self.test_bot())

    async def test_bot(self):
        try:
            self.stdout.write("🔧 Testing Telegram bot connection...")

            # Проверяем наличие токена
            if (
                not hasattr(settings, "TELEGRAM_BOT_TOKEN")
                or not settings.TELEGRAM_BOT_TOKEN
            ):
                self.stdout.write(
                    self.style.ERROR("❌ TELEGRAM_BOT_TOKEN not found in settings")
                )
                return

            self.stdout.write(f"✅ Token found: {settings.TELEGRAM_BOT_TOKEN[:10]}...")

            # Создаем бота
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

            # Получаем информацию о боте (асинхронно)
            bot_info = await bot.get_me()
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Bot: {bot_info.first_name} (@{bot_info.username})"
                )
            )
            self.stdout.write(f"✅ Bot ID: {bot_info.id}")

            # Получаем обновления (асинхронно)
            self.stdout.write("📨 Checking for messages...")
            updates = await bot.get_updates()

            if updates:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Found {len(updates)} message(s):")
                )
                for update in updates:
                    if update.message:
                        self.stdout.write("---")
                        self.stdout.write(f"Chat ID: {update.message.chat.id}")
                        self.stdout.write(
                            f"From: {update.message.from_user.first_name}"
                        )
                        self.stdout.write(f"Text: {update.message.text}")
            else:
                self.stdout.write("❌ No recent messages found")
                self.stdout.write(
                    "💡 Send a message to your bot in Telegram and "
                    "run this command again"
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
