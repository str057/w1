from rest_framework import serializers
from habits.models import Habit
from django.core.exceptions import ValidationError


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

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

    def validate(self, data):
        """Валидация на уровне сериализатора"""
        instance = Habit(**data)
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
