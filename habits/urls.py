from django.urls import path, include
from rest_framework.routers import DefaultRouter
from habits.views import HabitViewSet

# Определяем имя приложения для поддержки namespace
# Define app name for namespace support
app_name = "habits"

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habits")

urlpatterns = [
    path("", include(router.urls)),
]