from django.urls import path, include
from rest_framework.routers import DefaultRouter
from habits.views import HabitViewSet

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habits")

urlpatterns = [
    path("", include(router.urls)),
]
