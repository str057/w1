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
        self.other_user = User.objects.create_user(
            email="other@example.com", password="otherpass123"
        )

        self.habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="20:00:00",
            action="Read book",
            time_to_complete=120,
            periodicity=1,
        )

        # Создаем публичную привычку для тестирования
        self.public_habit = Habit.objects.create(
            user=self.other_user,
            place="Park",
            time="07:00:00",
            action="Morning run",
            time_to_complete=30,
            periodicity=1,
            is_public=True,
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
        self.assertEqual(Habit.objects.count(), 3)  # Увеличиваем ожидаемое количество

    def test_get_public_habits(self):
        """Тест получения публичных привычек"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/habits/public/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что публичная привычка доступна
        if "results" in response.data:
            self.assertEqual(len(response.data["results"]), 1)
            self.assertEqual(response.data["results"][0]["action"], "Morning run")
        else:
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]["action"], "Morning run")

    def test_update_habit(self):
        """Тест обновления привычки"""
        self.client.force_authenticate(user=self.user)
        data = {
            "place": "Library",
            "time": "21:00:00",
            "action": "Read technical book",
            "time_to_complete": 90,
            "periodicity": 2,
        }
        response = self.client.put(f"/api/habits/habits/{self.habit.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем обновленные данные
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.place, "Library")
        self.assertEqual(self.habit.action, "Read technical book")

    def test_update_other_user_habit(self):
        """Тест попытки обновления чужой привычки"""
        self.client.force_authenticate(user=self.other_user)
        data = {
            "place": "Library",
            "time": "21:00:00",
            "action": "Modified action",
        }
        response = self.client.put(f"/api/habits/habits/{self.habit.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_habit(self):
        """Тест удаления привычки"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/habits/habits/{self.habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 1)  # Остается только публичная привычка

    def test_delete_other_user_habit(self):
        """Тест попытки удаления чужой привычки"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f"/api/habits/habits/{self.habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_habit(self):
        """Тест получения конкретной привычки"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/habits/habits/{self.habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "Read book")

    def test_create_habit_validation(self):
        """Тест валидации при создании привычки"""
        self.client.force_authenticate(user=self.user)

        # Тест с некорректным временем выполнения (> 120 секунд)
        data = {
            "place": "Park",
            "time": "07:00:00",
            "action": "Morning run",
            "time_to_complete": 130,  # Превышает лимит
            "periodicity": 1,
        }
        response = self.client.post("/api/habits/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_periodicity_validation(self):
        """Тест валидации периодичности"""
        self.client.force_authenticate(user=self.user)

        data = {
            "place": "Park",
            "time": "07:00:00",
            "action": "Morning run",
            "time_to_complete": 120,
            "periodicity": 8,  # Превышает лимит
        }
        response = self.client.post("/api/habits/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
