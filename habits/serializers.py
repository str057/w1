from rest_framework import serializers
from habits.models import Habit
from django.core.exceptions import ValidationError


class HabitSerializer(serializers.ModelSerializer):
    # Проблема: HiddenField скрывает поле из вывода, а тесты ожидают его видеть
    # Решение: Используем PrimaryKeyRelatedField для отображения
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "time_to_complete",
            "is_public",
            "created_at",
        ]
        read_only_fields = ("id", "user", "created_at")

    def create(self, validated_data):
        """Переопределяем create, чтобы установить текущего пользователя"""
        # Получаем пользователя из контекста
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def validate(self, data):
        """Валидация на уровне сериализатора"""
        # Создаем временный экземпляр с текущими данными
        user = self.context.get('request').user if self.context.get('request') else None
        instance = Habit(user=user, **data)
        try:
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data


class PublicHabitSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Habit
        fields = [
            "id",
            "user_email",
            "place",
            "time",
            "action",
            "periodicity",
            "time_to_complete",
            "created_at",
        ]
        read_only_fields = fields