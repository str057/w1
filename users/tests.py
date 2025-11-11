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
        User.objects.create_user(email="tokenuser@example.com", password="testpass123")
        data = {"email": "tokenuser@example.com", "password": "testpass123"}
        response = self.client.post("/api/users/token/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
