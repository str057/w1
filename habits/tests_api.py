from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from habits.models import Habit
from users.models import User


class HabitAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.other_user = User.objects.create_user(email="other@example.com", password="otherpass123")

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

        # Создаем приятную привычку для тестирования связанных привычек
        self.pleasant_habit = Habit.objects.create(
            user=self.other_user,
            place="Home",
            time="21:00:00",
            action="Meditation",
            time_to_complete=60,
            periodicity=1,
            is_pleasant=True,
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
        self.assertEqual(Habit.objects.count(), 4)

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
        self.assertEqual(Habit.objects.count(), 2)

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
            "time_to_complete": 130,
            "periodicity": 1,
        }
        response = self.client.post("/api/habits/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_periodicity_validation(self):
        """Тест валидации периодичности"""
        self.client.force_authenticate(user=self.user)

        # Тест с некорректной периодичностью (> 7)
        data = {
            "place": "Park",
            "time": "07:00:00",
            "action": "Morning run",
            "time_to_complete": 120,
            "periodicity": 8,
        }
        response = self.client.post("/api/habits/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_related_habit_and_reward_validation(self):
        """Тест взаимной исключительности связанной привычки и вознаграждения"""
        self.client.force_authenticate(user=self.user)

        data = {
            "place": "Home",
            "time": "19:00:00",
            "action": "Test action",
            "time_to_complete": 120,
            "periodicity": 1,
            "related_habit": self.pleasant_habit.id,
            "reward": "Test reward",
        }
        response = self.client.post("/api/habits/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_related_habit_validation(self):
        """Тест что связанная привычка должна быть приятной"""
        self.client.force_authenticate(user=self.user)

        # Создаем НЕ приятную привычку
        non_pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Home",
            time="18:00:00",
            action="Study",
            time_to_complete=120,
            periodicity=1,
            is_pleasant=False,
        )

        data = {
            "place": "Home",
            "time": "19:00:00",
            "action": "Test action",
            "time_to_complete": 120,
            "periodicity": 1,
            "related_habit": non_pleasant_habit.id,
        }
        response = self.client.post("/api/habits/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pleasant_habit_validation(self):
        """Тест что у приятной привычки не может быть вознаграждения"""
        self.client.force_authenticate(user=self.user)

        data = {
            "place": "Home",
            "time": "19:00:00",
            "action": "Relax",
            "time_to_complete": 120,
            "periodicity": 1,
            "is_pleasant": True,
            "reward": "Test reward",
        }
        response = self.client.post("/api/habits/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_only_see_own_habits(self):
        """Тест что пользователь видит только свои привычки"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/habits/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if "results" in response.data:
            habits = response.data["results"]
        else:
            habits = response.data

        # Проверяем что все возвращенные привычки принадлежат пользователю
        for habit in habits:
            if isinstance(habit, dict):
                self.assertEqual(habit["user"], self.user.id)

    def test_partial_update_habit(self):
        """Тест частичного обновления привычки"""
        self.client.force_authenticate(user=self.user)
        data = {
            "action": "Updated action",
        }
        response = self.client.patch(f"/api/habits/habits/{self.habit.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем обновленные данные
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, "Updated action")

    def test_create_habit_with_related_habit(self):
        """Тест создания привычки со связанной привычкой"""
        self.client.force_authenticate(user=self.user)
        data = {
            "place": "Home",
            "time": "19:00:00",
            "action": "Evening routine",
            "time_to_complete": 120,
            "periodicity": 1,
            "related_habit": self.pleasant_habit.id,
        }
        response = self.client.post("/api/habits/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 4)

    def test_create_habit_with_reward(self):
        """Тест создания привычки с вознаграждением"""
        self.client.force_authenticate(user=self.user)
        data = {
            "place": "Home",
            "time": "19:00:00",
            "action": "Evening routine",
            "time_to_complete": 120,
            "periodicity": 1,
            "reward": "Watch TV",
        }
        response = self.client.post("/api/habits/habits/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 4)

    def test_habit_serializer_includes_all_fields(self):
        """Тест что сериализатор включает все необходимые поля"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/habits/habits/{self.habit.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "time_to_complete",
            "is_public",
            "created_at",
        ]

        for field in expected_fields:
            self.assertIn(field, response.data)

    def test_habit_list_pagination(self):
        """Тест пагинации списка привычек"""
        self.client.force_authenticate(user=self.user)

        # Создаем несколько привычек для тестирования пагинации
        for i in range(5):
            Habit.objects.create(
                user=self.user,
                place=f"Place {i}",
                time="20:00:00",
                action=f"Action {i}",
                time_to_complete=120,
                periodicity=1,
            )

        response = self.client.get("/api/habits/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем структуру пагинации
        if "results" in response.data:
            self.assertIn("count", response.data)
            self.assertIn("next", response.data)
            self.assertIn("previous", response.data)
            self.assertIn("results", response.data)
            # 1 исходная + 5 новых = 6 привычек
            self.assertEqual(len(response.data["results"]), 6)
            self.assertEqual(response.data["count"], 6)
        else:
            # Без пагинации - просто проверяем количество
            self.assertEqual(len(response.data), 6)

    def test_habit_ordering(self):
        """Тест сортировки привычек"""
        self.client.force_authenticate(user=self.user)

        # Создаем привычку с другим временем
        Habit.objects.create(
            user=self.user,
            place="Morning",
            time="07:00:00",
            action="Morning routine",
            time_to_complete=120,
            periodicity=1,
        )

        response = self.client.get("/api/habits/habits/?ordering=time")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if "results" in response.data:
            habits = response.data["results"]
            times = [habit["time"] for habit in habits]
            self.assertEqual(times, sorted(times))
        else:
            times = [habit["time"] for habit in response.data]
            self.assertEqual(times, sorted(times))

    def test_habit_str_method(self):
        """Тест строкового представления привычки"""
        self.assertEqual(str(self.habit), "Read book at 20:00:00")

    def test_habit_model_fields(self):
        """Тест полей модели Habit"""
        self.assertEqual(self.habit.user, self.user)
        self.assertEqual(self.habit.place, "Home")
        self.assertEqual(self.habit.time, "20:00:00")
        self.assertEqual(self.habit.action, "Read book")
        self.assertEqual(self.habit.time_to_complete, 120)
        self.assertEqual(self.habit.periodicity, 1)
        self.assertFalse(self.habit.is_pleasant)
        self.assertFalse(self.habit.is_public)
        self.assertIsNone(self.habit.related_habit)
        self.assertIsNone(self.habit.reward)
        self.assertIsNotNone(self.habit.created_at)