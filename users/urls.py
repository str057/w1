from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import UserViewSet, PaymentViewSet, UserProfileView, LoginView

app_name = UsersConfig.name


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("", include(router.urls)),
    # Аутентификация
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login/", LoginView.as_view(), name="login"),
    # Профиль
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("profile/<int:pk>/", UserProfileView.as_view(), name="profile_detail"),
]
