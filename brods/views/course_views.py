from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema

from users.permissions import IsModerator, IsNotModerator, IsOwner
from brods.models import Course, Subscription
from brods.serializers import (
    CourseSerializer,
    CourseDetailSerializer,
)


@extend_schema(tags=["Курсы"])
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["owner"]

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

    @extend_schema(
        summary="Создать курс",
        description="Создание нового курса. Модераторы не могут создавать курсы.",
    )
    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name="moderators").exists():
            return Response(
                {"detail": "Модераторы не могут создавать курсы"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary="Удалить курс",
        description="Удаление курса. Модераторы не могут удалять курсы.",
    )
    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name="moderators").exists():
            return Response(
                {"detail": "Модераторы не могут удалять курсы"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Подписаться/отписаться от курса",
        description="Переключает подписку пользователя на курс",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "subscribed": {"type": "boolean"},
                },
            }
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Подписка/отписка от курса"""
        course = self.get_object()
        user = request.user

        subscription, created = Subscription.objects.get_or_create(
            user=user, course=course
        )

        if created:
            message = "Подписка оформлена"
            subscribed = True
        else:
            subscription.delete()
            message = "Подписка отменена"
            subscribed = False

        return Response(
            {"message": message, "subscribed": subscribed}, status=status.HTTP_200_OK
        )
