from django.db import models
from django.conf import settings


class TelegramUser(models.Model):
    """Model for storing Telegram user data"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegram"
    )
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Telegram username"
    )
    first_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="First name in Telegram"
    )
    chat_id = models.BigIntegerField(verbose_name="Chat ID for messages")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"

    def __str__(self):
        return f"{self.user.email} - {self.telegram_id}"
