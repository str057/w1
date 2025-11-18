from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Habit(models.Model):
    PERIOD_CHOICES = [
        (1, "Ежедневно"),
        (2, "Раз в 2 дня"),
        (3, "Раз в 3 дня"),
        (4, "Раз в 4 дня"),
        (5, "Раз в 5 дней"),
        (6, "Раз в 6 дней"),
        (7, "Раз в неделю"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    place = models.CharField(max_length=255, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.CharField(max_length=255, verbose_name="Действие")
    is_pleasant = models.BooleanField(
        default=False, verbose_name="Признак приятной привычки"
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
    )
    periodicity = models.PositiveIntegerField(
        choices=PERIOD_CHOICES, default=1, verbose_name="Периодичность"
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,  # Добавлено null=True
        verbose_name="Вознаграждение",
    )
    time_to_complete = models.PositiveIntegerField(
        verbose_name="Время на выполнение (секунды)"
    )
    is_public = models.BooleanField(default=False, verbose_name="Признак публичности")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} at {self.time}"  # Исправлено строковое представление

    def clean(self):
        """Валидация данных перед сохранением"""
        errors = {}

        # 1. Исключить одновременный выбор связанной привычки и вознаграждения
        if self.related_habit and self.reward:
            error_msg = (
                "Нельзя указывать одновременно связанную привычку и вознаграждение"
            )
            errors["reward"] = error_msg
            errors["related_habit"] = error_msg

        # 2. Время выполнения должно быть не больше 120 секунд
        if self.time_to_complete > 120:
            errors["time_to_complete"] = (
                "Время выполнения не может превышать 120 секунд"
            )

        # 3. В связанные привычки могут попадать только привычки
        # с признаком приятной привычки
        if self.related_habit and not self.related_habit.is_pleasant:
            errors["related_habit"] = "Связанная привычка должна быть приятной"

        # 4. У приятной привычки не может быть вознаграждения
        # или связанной привычки
        if self.is_pleasant:
            if self.reward:  # Проверяем не пустую строку или None
                errors["reward"] = "У приятной привычки не может быть вознаграждения"
            if self.related_habit:
                errors["related_habit"] = (
                    "У приятной привычки не может быть связанной привычки"
                )

        # 5. Периодичность от 1 до 7 дней
        if self.periodicity not in [1, 2, 3, 4, 5, 6, 7]:
            errors["periodicity"] = "Периодичность должна быть от 1 до 7 дней"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Вызываем валидацию перед сохранением"""
        self.clean()
        super().save(*args, **kwargs)
