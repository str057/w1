from django.core.management.base import BaseCommand
from users.models import User, TelegramUser


class Command(BaseCommand):
    help = "Link Telegram user to Django user"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="User email")
        parser.add_argument("telegram_id", type=int, help="Telegram chat ID")

    def handle(self, *args, **options):
        email = options["email"]
        telegram_id = options["telegram_id"]

        try:
            user = User.objects.get(email=email)
            TelegramUser.objects.get_or_create(
                user=user,
                defaults={
                    "telegram_id": telegram_id,
                    "telegram_username": f"user_{telegram_id}",
                },
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ User {email} linked to Telegram ID {telegram_id}"
                )
            )
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ User with email {email} not found"))
