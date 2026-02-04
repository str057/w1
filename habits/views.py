from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from habits.models import Habit
from habits.serializers import HabitSerializer, PublicHabitSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользователь может изменять/удалять только свои привычки.
    Для безопасных методов (GET, HEAD, OPTIONS) разрешено всем.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы для всех
        if request.method in permissions.SAFE_METHODS:
            return True
        # Проверяем, что пользователь - владелец привычки
        return obj.user == request.user


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для управления привычками"""

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_pleasant", "is_public", "periodicity"]

    def get_queryset(self):
        """
        Возвращаем привычки:
        - Для обычных запросов: только привычки текущего пользователя
        - Для публичного эндпоинта: только публичные привычки
        """
        user = self.request.user

        if self.action == "public":
            # Для публичного эндпоинта показываем только публичные привычки
            return Habit.objects.filter(is_public=True)

        # Для обычных запросов показываем привычки текущего пользователя
        # ИЛИ публичные привычки других пользователей
        if user.is_authenticated:
            return Habit.objects.filter(Q(user=user) | Q(is_public=True))
        return Habit.objects.none()

    def get_serializer_class(self):
        if self.action == "public":
            return PublicHabitSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        """Автоматически назначаем текущего пользователя при создании привычки"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def public(self, request):
        """Список публичных привычек"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Переопределяем retrieve для проверки доступа к чужой привычке"""
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Habit.DoesNotExist:
            return Response(
                {"detail": "Привычка не найдена."},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied:
            # Если привычка существует, но пользователь не владелец
            return Response(
                {"detail": "У вас нет прав для доступа к этой привычке."},
                status=status.HTTP_403_FORBIDDEN
            )