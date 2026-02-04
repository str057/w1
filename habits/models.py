from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

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
        choices=PERIOD_CHOICES,
        default=1,
        verbose_name="Периодичность",
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Вознаграждение",
    )
    time_to_complete = models.PositiveIntegerField(
        verbose_name="Время на выполнение (секунды)",
        validators=[MinValueValidator(1), MaxValueValidator(120)]
    )
    is_public = models.BooleanField(default=False, verbose_name="Признак публичности")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} в {self.time}"

    def clean(self):
        """Валидация данных перед сохранением"""
        errors = {}

        # 1. Исключить одновременный выбор связанной привычки и вознаграждения
        if self.related_habit and self.reward and self.reward.strip():
            errors["reward"] = "Нельзя указывать одновременно связанную привычку и вознаграждение"
            errors["related_habit"] = "Нельзя указывать одновременно связанную привычку и вознаграждение"

        # 2. В связанные привычки могут попадать только привычки с признаком приятной привычки
        if self.related_habit and not self.related_habit.is_pleasant:
            errors["related_habit"] = "Связанная привычка должна быть приятной"

        # 3. У приятной привычки не может быть вознаграждения или связанной привычки
        if self.is_pleasant:
            if self.reward and self.reward.strip():
                errors["reward"] = "У приятной привычки не может быть вознаграждения"
            if self.related_habit:
                errors["related_habit"] = "У приятной привычки не может быть связанной привычки"

        # 4. Нельзя ссылаться на себя как на связанную привычку
        if self.related_habit and self.related_habit.id == self.id:
            errors["related_habit"] = "Привычка не может ссылаться на саму себя"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Вызываем валидацию перед сохранением"""
        self.full_clean()
        super().save(*args, **kwargs)