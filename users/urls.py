from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from users.views import UserCreateAPIView

app_name = "users"

urlpatterns = [
    # Регистрация пользователя
    path("register/", UserCreateAPIView.as_view(), name="register"),
    # JWT аутентификация
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
