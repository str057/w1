from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from habits.models import Habit
from habits.serializers import HabitSerializer, PublicHabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для управления привычками"""

    serializer_class = HabitSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_pleasant", "is_public", "periodicity"]

    def get_queryset(self):
        if self.action == "public":
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "public":
            return PublicHabitSerializer
        return HabitSerializer

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
