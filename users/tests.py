from django.test import TestCase
from rest_framework import status
from users.models import User


class UserAPITestCase(TestCase):
    def test_user_registration(self):
        """Тест регистрации пользователя"""
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post("/api/users/register/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "newuser@example.com")
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_jwt_token_obtain(self):
        """Тест получения JWT токена"""
        # Создаем пользователя для теста
        User.objects.create_user(email="tokenuser@example.com", password="testpass123")

        data = {"email": "tokenuser@example.com", "password": "testpass123"}

        response = self.client.post("/api/users/token/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


class UserModelTest(TestCase):
    def test_create_user(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertEqual(user.first_name, "Test")

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
