from django.urls import path, include
from rest_framework.routers import DefaultRouter
from brods.views import CourseViewSet, LessonViewSet


router = DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"lessons", LessonViewSet)



urlpatterns = [
    path("", include(router.urls)),
]
