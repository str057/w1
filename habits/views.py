from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

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
        - Для list запросов: только привычки текущего пользователя
        - Для остальных действий: все привычки (права проверяются)
        """
        user = self.request.user

        # Для списка привычек пользователь видит только свои
        if self.action == "list":
            if user.is_authenticated:
                return Habit.objects.filter(user=user)
            return Habit.objects.none()

        # Для других действий - все привычки
        return Habit.objects.all()

    def get_serializer_class(self):
        if self.action == "public":
            return PublicHabitSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        """Автоматически назначаем текущего пользователя при создании привычки"""
        serializer.save(user=self.request.user)

    # ЯВНО определяем public action с правильными параметрами
    @action(detail=False, methods=['get'], url_path='public', url_name='public',
            permission_classes=[permissions.AllowAny])
    def public(self, request):
        """Список публичных привычек - доступен без аутентификации"""
        queryset = Habit.objects.filter(is_public=True)
        queryset = self.filter_queryset(queryset)

        # Добавляем пагинацию как в стандартном list
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)