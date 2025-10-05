import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Create default user groups"

    def handle(self, *args, **options):
        # Создаем группу модераторов
        moderator_group, created = Group.objects.get_or_create(name="moderators")

        if created:
            self.stdout.write(
                self.style.SUCCESS("✅ Группа модераторов успешно создана")
            )
        else:
            self.stdout.write(self.style.WARNING("ℹ️ Группа модераторов уже существует"))
