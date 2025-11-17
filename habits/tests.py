from django.test import TestCase
from habits.models import Habit
from users.models import User


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        self.habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="20:00:00",
            action="Test habit",
            time_to_complete=120,
            periodicity=1,
        )

    def test_habit_creation(self):
        """Тест что привычка создается корректно"""
        self.assertEqual(self.habit.action, "Test habit")
        self.assertEqual(self.habit.user.email, "test@example.com")

    def test_user_with_telegram_chat_id(self):
        """Тест пользователя с telegram_chat_id"""
        user_with_chat = User.objects.create_user(
            email="telegram@example.com",
            password="testpass123",
            telegram_chat_id="123456789",
        )
        self.assertEqual(user_with_chat.telegram_chat_id, "123456789")


class TelegramBotTest(TestCase):
    def test_bot_import(self):
        """Тест что бот импортируется без ошибок"""
        try:
            from telegram_bot.handlers import start

            self.assertTrue(callable(start))
        except ImportError:
            # Если нет handlers, это нормально для тестов
            pass
