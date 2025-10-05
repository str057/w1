from django.core.management.base import BaseCommand
from users.models import User, Payment
from brods.models import Course, Lesson
from decimal import Decimal
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Заполняет базу данных тестовыми платежами"

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        courses = Course.objects.all()
        lessons = Lesson.objects.all()

        if not users.exists():
            self.stdout.write(
                self.style.ERROR("Необходимо сначала создать пользователей")
            )
            return

        Payment.objects.all().delete()

        payment_methods = ["cash", "transfer"]
        amounts_courses = [Decimal("1000.00"), Decimal("1500.00"), Decimal("2000.00")]
        amounts_lessons = [Decimal("300.00"), Decimal("500.00")]

        payments_created = 0

        if courses.exists():
            for user in users[:3]:
                for course in courses[:2]:
                    Payment.objects.create(
                        user=user,
                        paid_course=course,
                        paid_lesson=None,
                        amount=random.choice(amounts_courses),
                        payment_method=random.choice(payment_methods),
                        payment_date=datetime.now()
                        - timedelta(days=random.randint(1, 30)),
                    )
                    payments_created += 1

        if lessons.exists():
            user_slice = users[3:5] if len(users) > 4 else users
            for user in user_slice:
                for lesson in lessons[:3]:
                    Payment.objects.create(
                        user=user,
                        paid_course=None,
                        paid_lesson=lesson,
                        amount=random.choice(amounts_lessons),
                        payment_method=random.choice(payment_methods),
                        payment_date=datetime.now()
                        - timedelta(days=random.randint(1, 30)),
                    )
                    payments_created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Успешно создано {payments_created} тестовых платежей")
        )
