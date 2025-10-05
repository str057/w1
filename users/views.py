from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from rest_framework import filters

from users.models import Payment, User
from users.serializers import (
    PaymentSerializer,
    UserProfileSerializer,
    UserProfilePublicSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
from users.permissions import IsModerator, IsOwner, IsProfileOwner


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegisterSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            # Регистрация доступна всем
            return [permissions.AllowAny()]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Изменение и удаление - только владельцу
            return [permissions.IsAuthenticated(), IsProfileOwner()]
        elif self.action in ["list", "retrieve"]:
            # Просмотр - авторизованным пользователям
            return [permissions.IsAuthenticated()]
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        """Регистрация пользователя"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерируем токены для автоматического входа после регистрации
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payment.objects.none()

        if user.groups.filter(name="moderators").exists():
            # Модераторы видят все платежи
            return Payment.objects.all()
        else:
            # Обычные пользователи видят только свои платежи
            return Payment.objects.filter(user=user)

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), ~IsModerator()]
        elif self.action == "list":
            return [permissions.IsAuthenticated()]
        elif self.action == "retrieve":
            return [permissions.IsAuthenticated(), IsModerator() | IsOwner()]
        elif self.action in ["update", "partial_update"]:
            return [permissions.IsAuthenticated(), IsOwner()]
        elif self.action == "destroy":
            return [permissions.IsAuthenticated(), IsOwner(), ~IsModerator()]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Профиль пользователя - просмотр и редактирование"""

    def get_serializer_class(self):
        if self.request.method == "GET":
            # Для GET запроса определяем сериализатор в зависимости от того,
            # смотрит ли пользователь свой профиль или чужой
            if self.kwargs.get("pk") == str(self.request.user.pk) or self.kwargs.get(
                "pk"
            ) in [None, "me"]:
                return UserProfileSerializer
            else:
                return UserProfilePublicSerializer
        else:
            # Для PUT/PATCH запросов - только полный сериализатор
            return UserProfileSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            # Просмотр профиля доступен всем авторизованным пользователям
            return [permissions.IsAuthenticated()]
        else:
            # Редактирование - только владельцу профиля
            return [permissions.IsAuthenticated(), IsProfileOwner()]

    def get_object(self):
        # Если pk не указан или указан как 'me', возвращаем текущего пользователя
        pk = self.kwargs.get("pk")
        if pk is None or pk == "me":
            return self.request.user
        return User.objects.get(pk=pk)


class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email и пароль обязательны"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                }
            )

        return Response(
            {"error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED
        )
