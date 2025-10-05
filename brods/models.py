from django.db import models
from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=150, verbose_name="Название")
    preview = models.ImageField(
        upload_to="courses/previews/", blank=True, null=True, verbose_name="Превью"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        null=True,
        blank=True,
        related_name="courses",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=150, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    preview = models.ImageField(
        upload_to="lessons/previews/", blank=True, null=True, verbose_name="Превью"
    )
    video_link = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        null=True,
        blank=True,
        related_name="lessons",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.title
