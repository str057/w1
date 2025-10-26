from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    preview = models.ImageField(
        upload_to="courses/previews/",
        blank=True,
        null=True,
        verbose_name="Превью",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="brods_courses",
        verbose_name="Владелец",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Цена",
    )
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    stripe_product_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Stripe Product ID",
    )
    stripe_price_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Stripe Price ID",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.price < 0:
            raise ValidationError({"price": "Цена не может быть отрицательной"})

    @property
    def lessons_count(self):
        """Количество уроков в курсе"""
        return self.lessons.count()


class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    preview = models.ImageField(
        upload_to="lessons/previews/",
        blank=True,
        null=True,
        verbose_name="Превью",
    )
    video_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="brods_lessons",
        verbose_name="Владелец",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["order", "created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.order < 0:
            raise ValidationError({"order": "Порядок не может быть отрицательным"})


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="brods_subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ["user", "course"]

    def __str__(self):
        status = "активна" if self.is_active else "неактивна"
        return f"{self.user.email} - {self.course.title} ({status})"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
        ("stripe", "Stripe"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Ожидает оплаты"),
        ("paid", "Оплачено"),
        ("failed", "Ошибка оплаты"),
        ("refunded", "Возврат"),
        ("canceled", "Отменен"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="brods_payments",
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный курс",
        related_name="payments",
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный урок",
        related_name="payments",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма оплаты"
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Способ оплаты",
    )
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
        verbose_name="Статус оплаты",
    )
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Stripe Session ID",
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Stripe Payment Intent ID",
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]

    def __str__(self):
        if self.paid_course:
            item = self.paid_course.title
        elif self.paid_lesson:
            item = self.paid_lesson.title
        else:
            item = "неизвестный предмет"
        return (
            f"Платеж {self.user.email} - {self.amount} за {item} "
            f"({self.get_payment_status_display()})"
        )

    def clean(self):
        if self.paid_course and self.paid_lesson:
            raise ValidationError(
                "Можно указать только курс ИЛИ урок, но не оба одновременно."
            )
        if not self.paid_course and not self.paid_lesson:
            raise ValidationError("Должен быть указан либо курс, либо урок.")
        if self.amount <= 0:
            raise ValidationError({"amount": "Сумма оплаты должна быть положительной"})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def paid_item(self):
        """Возвращает оплаченный предмет (курс или урок)"""
        return self.paid_course or self.paid_lesson
