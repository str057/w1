from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema

from users.permissions import IsModerator, IsNotModerator, IsOwner
from brods.models import Lesson
from brods.serializers import (
    LessonSerializer,
    LessonListSerializer,
)


@extend_schema(tags=["Уроки"])
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["course", "owner"]

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

    @extend_schema(
        summary="Создать урок",
        description="Создание нового урока. Модераторы не могут создавать уроки.",
    )
    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name="moderators").exists():
            return Response(
                {"detail": "Модераторы не могут создавать уроки"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary="Удалить урок",
        description="Удаление урока. Модераторы не могут удалять уроки.",
    )
    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name="moderators").exists():
            return Response(
                {"detail": "Модераторы не могут удалять уроки"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
