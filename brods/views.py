from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsModerator, IsNotModerator, IsOwner
from brods.models import Course, Lesson
from brods.serializers import (
    CourseSerializer,
    CourseDetailSerializer,
    LessonSerializer,
    LessonListSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if (
            self.request.user.is_authenticated
            and not self.request.user.groups.filter(name="moderators").exists()
        ):
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, IsNotModerator]
        elif self.action == "list":
            self.permission_classes = [IsAuthenticated]
        elif self.action == "retrieve":
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action in ["update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, IsOwner, IsNotModerator]
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        # Явная проверка для модераторов
        if request.user.groups.filter(name="moderators").exists():
            return Response(
                {"detail": "Модераторы не могут создавать курсы"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Явная проверка для модераторов при удалении
        if request.user.groups.filter(name="moderators").exists():
            return Response(
                {"detail": "Модераторы не могут удалять курсы"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return LessonListSerializer
        return LessonSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if (
            self.request.user.is_authenticated
            and not self.request.user.groups.filter(name="moderators").exists()
        ):
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, IsNotModerator]
        elif self.action == "list":
            self.permission_classes = [IsAuthenticated]
        elif self.action == "retrieve":
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action in ["update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, IsOwner, IsNotModerator]
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        # Явная проверка для модераторов
        if request.user.groups.filter(name="moderators").exists():
            return Response(
                {"detail": "Модераторы не могут создавать уроки"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        # Явная проверка для модераторов при удалении
        if request.user.groups.filter(name="moderators").exists():
            return Response(
                {"detail": "Модераторы не могут удалять уроки"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
