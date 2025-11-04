from django.test import TestCase
from django.core.exceptions import ValidationError
from habits.models import Habit
from users.models import User


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    def test_create_habit(self):
        """Тест создания привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="20:00:00",
            action="Read book",
            time_to_complete=120,
            periodicity=1,
        )

        self.assertEqual(habit.action, "Read book")
        self.assertEqual(habit.user.email, "test@example.com")

    def test_habit_str_method(self):
        """Тест строкового представления привычки"""
        habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="20:00:00",
            action="Test habit",
            time_to_complete=120,
            periodicity=1,
        )

        self.assertIn("Test habit", str(habit))


class HabitValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    def test_time_to_complete_validation(self):
        """Тест валидации времени выполнения"""
        habit = Habit(
            user=self.user,
            place="Home",
            time="20:00:00",
            action="Test habit",
            time_to_complete=121,  # Больше 120 секунд
            periodicity=1,
        )

        with self.assertRaises(ValidationError):
            habit.full_clean()
