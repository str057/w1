from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from brods.models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTestCase(APITestCase):
    def setUp(self):
        # Создаем пользователей БЕЗ username
        self.owner_user = User.objects.create_user(
            email="owner@test.com", password="testpass123"
        )
        self.moderator_user = User.objects.create_user(
            email="moderator@test.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            email="other@test.com", password="testpass123"
        )

        # Создаем группу модераторов и добавляем пользователя
        from django.contrib.auth.models import Group

        moderators_group, _ = Group.objects.get_or_create(name="moderators")
        self.moderator_user.groups.add(moderators_group)

        # Создаем курс и урок
        self.course = Course.objects.create(
            title="Test Course", description="Test Description", owner=self.owner_user
        )

        self.lesson_data = {
            "title": "Test Lesson",
            "description": "Valid YouTube link: https://www.youtube.com/watch?v=test",
            "course": self.course.id,
        }

    def test_create_lesson_by_owner(self):
        """Тест создания урока владельцем"""
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.post("/api/lessons/", self.lesson_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_create_lesson_by_moderator(self):
        """Тест создания урока модератором (должен быть запрещен)"""
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.post("/api/lessons/", self.lesson_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_with_invalid_url(self):
        """Тест создания урока с запрещенной ссылкой"""
        self.client.force_authenticate(user=self.owner_user)
        invalid_data = self.lesson_data.copy()
        invalid_data["description"] = "Invalid link: https://vk.com/test"
        response = self.client.post("/api/lessons/", invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_lesson_by_owner(self):
        """Тест обновления урока владельцем"""
        lesson = Lesson.objects.create(
            title="Original Lesson",
            description="Original Description",
            course=self.course,
            owner=self.owner_user,
        )
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.patch(
            f"/api/lessons/{lesson.id}/", {"title": "Updated Lesson"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lesson.refresh_from_db()
        self.assertEqual(lesson.title, "Updated Lesson")

    def test_delete_lesson_by_owner(self):
        """Тест удаления урока владельцем"""
        lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Test Description",
            course=self.course,
            owner=self.owner_user,
        )
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.delete(f"/api/lessons/{lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_by_moderator(self):
        """Тест удаления урока модератором (должен быть запрещен)"""
        lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Test Description",
            course=self.course,
            owner=self.owner_user,
        )
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.delete(f"/api/lessons/{lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        # Создаем пользователя БЕЗ username
        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123"
        )
        self.course = Course.objects.create(
            title="Test Course", description="Test Description", owner=self.user
        )

    def test_subscribe_to_course(self):
        """Тест подписки на курс"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/subscription/", {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        # Сначала подписываемся
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/subscription/", {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscription_status_in_course_serializer(self):
        """Тест отображения статуса подписки в сериализаторе курса"""
        # Создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/courses/{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])


class PaginationTestCase(APITestCase):
    def setUp(self):
        # Создаем пользователя БЕЗ username
        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123"
        )

        # Создаем несколько курсов для тестирования пагинации
        for i in range(15):
            Course.objects.create(
                title=f"Course {i}", description=f"Description {i}", owner=self.user
            )

    def test_course_pagination(self):
        """Тест пагинации курсов"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 10)

    def test_lesson_pagination(self):
        """Тест пагинации уроков"""
        course = Course.objects.first()

        # Создаем несколько уроков
        for i in range(15):
            Lesson.objects.create(
                title=f"Lesson {i}",
                description=f"Description {i}",
                course=course,
                owner=self.user,
            )

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 10)
