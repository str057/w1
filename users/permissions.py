from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="moderators").exists()
        )


class IsNotModerator(permissions.BasePermission):
    """Проверяет, что пользователь НЕ является модератором"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and not request.user.groups.filter(name="moderators").exists()
        )


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        # Проверяем, есть ли у объекта атрибут 'user'
        if hasattr(obj, "user"):
            return obj.user == request.user
        # Если у объекта нет атрибута 'user', проверяем атрибут 'owner'
        elif hasattr(obj, "owner"):
            return obj.owner == request.user
        # Если нет ни того ни другого, возвращаем False
        return False


class IsProfileOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем профиля"""

    def has_object_permission(self, request, view, obj):
        # Для профиля пользователя сравниваем объект с request.user
        return obj == request.user
