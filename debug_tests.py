import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from habits.models import Habit

User = get_user_model()

print("=== ЗАПУСК ДИАГНОСТИКИ ТЕСТОВ ===")

# Создаем тестовую среду
class DebugTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='otherpass'
        )
        
        # Создаем привычку для тестового пользователя
        self.habit = Habit.objects.create(
            user=self.user,
            place='Home',
            time='20:00:00',
            action='Read book',
            time_to_complete=120,
            is_public=False
        )
        
        # Создаем чужую приватную привычку
        self.other_habit = Habit.objects.create(
            user=self.other_user,
            place='Office',
            time='09:00:00',
            action='Work',
            time_to_complete=90,
            is_public=False
        )
        
        # Создаем чужую публичную привычку
        self.public_habit = Habit.objects.create(
            user=self.other_user,
            place='Park',
            time='15:00:00',
            action='Running',
            time_to_complete=30,
            is_public=True
        )

    def test_1_time_comparison(self):
        """Проверка сравнения времени"""
        print("\n1. Тест сравнения времени:")
        print(f"   self.habit.time: {self.habit.time}")
        print(f"   str(self.habit.time): '{str(self.habit.time)}'")
        print(f"   Ожидается: '20:00:00'")
        try:
            self.assertEqual(str(self.habit.time), "20:00:00")
            print("   ✓ Тест проходит")
        except AssertionError as e:
            print(f"   ✗ Ошибка: {e}")

    def test_2_public_endpoint(self):
        """Проверка публичного эндпоинта"""
        print("\n2. Тест публичного эндпоинта:")
        response = self.client.get('/api/habits/habits/public/')
        print(f"   URL: /api/habits/habits/public/")
        print(f"   Status: {response.status_code}")
        print(f"   Ожидается: {status.HTTP_200_OK}")
        
        if response.status_code == 200:
            print("   ✓ Эндпоинт работает")
            if 'results' in response.data:
                print(f"   Найдено привычек: {len(response.data['results'])}")
                print(f"   Должна быть только публичная чужая привычка")
            else:
                print(f"   Данные: {response.data}")
        else:
            print(f"   ✗ Ошибка: {response.data}")

    def test_3_access_other_user_habit(self):
        """Проверка доступа к чужой привычке"""
        print("\n3. Тест доступа к чужой привычке:")
        
        self.client.force_authenticate(user=self.user)
        
        # Пытаемся получить чужую приватную привычку
        print(f"   а) Чужая приватная привычка (ID: {self.other_habit.id}):")
        response = self.client.get(f'/api/habits/habits/{self.other_habit.id}/')
        print(f"      Status: {response.status_code}")
        print(f"      Ожидается: {status.HTTP_403_FORBIDDEN} или {status.HTTP_404_NOT_FOUND}")
        
        if response.status_code in [403, 404]:
            print(f"      ✓ Возвращает правильный статус")
        else:
            print(f"      ✗ Неожиданный статус")
        
        # Пытаемся получить чужую публичную привычку
        print(f"   б) Чужая публичная привычка (ID: {self.public_habit.id}):")
        response = self.client.get(f'/api/habits/habits/{self.public_habit.id}/')
        print(f"      Status: {response.status_code}")
        print(f"      Ожидается: {status.HTTP_200_OK} (публичная)")
        
        if response.status_code == 200:
            print(f"      ✓ Доступ разрешен к публичной привычке")
        else:
            print(f"      ✗ Ошибка доступа к публичной привычке")

    def test_4_update_other_user_habit(self):
        """Проверка обновления чужой привычки"""
        print("\n4. Тест обновления чужой привычки:")
        
        self.client.force_authenticate(user=self.user)
        
        data = {"action": "Updated action"}
        response = self.client.patch(
            f'/api/habits/habits/{self.other_habit.id}/',
            data=data,
            format='json'
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Ожидается: {status.HTTP_403_FORBIDDEN}")
        
        if response.status_code == 403:
            print("   ✓ Возвращает 403 - правильно!")
        elif response.status_code == 404:
            print("   ⚠ Возвращает 404 - привычка скрыта")
        else:
            print(f"   ✗ Неожиданный статус: {response.status_code}")

    def run_all_tests(self):
        """Запуск всех диагностических тестов"""
        self.setUp()
        self.test_1_time_comparison()
        self.test_2_public_endpoint()
        self.test_3_access_other_user_habit()
        self.test_4_update_other_user_habit()

if __name__ == '__main__':
    debug = DebugTests()
    debug.run_all_tests()
    print("\n=== ДИАГНОСТИКА ЗАВЕРШЕНА ===")
