from django.core.management.base import BaseCommand
from habits.tasks import send_habit_reminders


class Command(BaseCommand):
    help = "Тестирование отправки напоминаний"

    def handle(self, *args, **options):
        self.stdout.write("🔔 Тестирование отправки напоминаний...")
        send_habit_reminders.delay()
        self.stdout.write(self.style.SUCCESS("✅ Задача отправки напоминаний запущена"))
