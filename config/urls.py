from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users.views import user_profile

urlpatterns = [
    path("admin/", admin.site.urls),
    # Добавляем namespace для habits приложения
    # Added namespace for habits app
    path("api/habits/", include("habits.urls", namespace="habits")),

    # Добавляем namespace для users приложения
    # Added namespace for users app
    path("api/users/", include("users.urls", namespace="users")),

    path("api/users/profile/", user_profile, name="user-profile"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]