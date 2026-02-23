from rest_framework import serializers
from habits.models import Habit
from django.core.exceptions import ValidationError


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = "__all__"  # Используем __all__ для гарантии включения всех полей
        read_only_fields = ("id", "user", "created_at")

    def create(self, validated_data):
        """Автоматически назначаем текущего пользователя при создании"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def validate(self, data):
        """Валидация на уровне сериализатора"""
        # Получаем текущий экземпляр (если есть) для обновления
        instance = getattr(self, 'instance', None)

        if instance:
            # Для обновления: создаем копию экземпляра с новыми данными
            for attr, value in data.items():
                setattr(instance, attr, value)
            try:
                instance.clean()
            except ValidationError as e:
                raise serializers.ValidationError(e.message_dict)
        else:
            # Для создания: создаем новый экземпляр
            user = self.context.get('request').user
            # Устанавливаем значения по умолчанию для обязательных полей
            defaults = {
                'user': user,
                'periodicity': 1,  # значение по умолчанию
                'time_to_complete': 60,  # значение по умолчанию
            }
            # Объединяем defaults с data
            instance_data = {**defaults, **data}
            instance = Habit(**instance_data)
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