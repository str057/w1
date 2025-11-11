from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from habits.models import Habit
from users.models import User


class HabitAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        self.habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="20:00:00",
            action="Read book",
            time_to_complete=120,
            periodicity=1,
        )

    def test_get_habits_authenticated(self):
        """Тест получения привычек с авторизацией"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/habits/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Исправленная проверка - смотрим на количество результатов
        if "results" in response.data:
            # Если используется пагинация
            self.assertEqual(len(response.data["results"]), 1)
        else:
            # Если возвращается просто список
            self.assertEqual(len(response.data), 1)

    def test_get_habits_unauthenticated(self):
        """Тест получения привычек без авторизации"""
        response = self.client.get("/api/habits/habits/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_habit(self):
        """Тест создания привычки"""
        self.client.force_authenticate(user=self.user)
        data = {
            "place": "Park",
            "time": "07:00:00",
            "action": "Morning run",
            "time_to_complete": 120,
            "periodicity": 1,
        }
        response = self.client.post("/api/habits/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)
