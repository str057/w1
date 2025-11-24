from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer

User = get_user_model()


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя"""

    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


@api_view(["GET"])
def user_profile(request):
    """Профиль текущего пользователя"""
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    return Response(
        {"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED
    )
