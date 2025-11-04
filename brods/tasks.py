from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Course, Subscription, Lesson
from users.models import User


@shared_task
def send_course_update_notification(course_id):
    """
    Асинхронная рассылка писем об обновлении курса
    """
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(
            course=course, is_active=True
        ).select_related("user")

        recipients = [sub.user.email for sub in subscriptions if sub.user.email]

        if not recipients:
            return f"No subscribers for course {course.title}"

        subject = f"Обновление курса: {course.title}"
        message = f"""
        Здравствуйте!

        Курс "{course.title}" был обновлен.

        Новые материалы уже доступны для изучения.

        Ссылка на курс: http://your-site.com/courses/{course.id}/

        С уважением,
        Команда образовательной платформы
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

        return (
            f"Sent update notifications to {len(recipients)} "
            f"subscribers for course {course.title}"
        )

    except Course.DoesNotExist:
        return f"Course with id {course_id} does not exist"
    except Exception as e:
        return f"Error sending notifications: {str(e)}"


@shared_task
def send_lesson_update_notification(lesson_id, course_id):
    """
    Асинхронная рассылка писем об обновлении урока
    с проверкой времени последнего обновления курса
    """
    try:
        course = Course.objects.get(id=course_id)
        lesson = Lesson.objects.get(id=lesson_id)

        # Проверка: отправляем уведомление только если курс не обновлялся более 4 часов
        four_hours_ago = timezone.now() - timedelta(hours=4)
        if course.updated_at and course.updated_at > four_hours_ago:
            return (
                f"Course {course.title} was updated recently, " "skipping notification"
            )

        subscriptions = Subscription.objects.filter(
            course=course, is_active=True
        ).select_related("user")

        recipients = [sub.user.email for sub in subscriptions if sub.user.email]

        if not recipients:
            return f"No subscribers for course {course.title}"

        subject = f"Новый урок в курсе: {course.title}"
        message = f"""
        Здравствуйте!

        В курсе "{course.title}" добавлен новый урок: "{lesson.title}".

        Новые материалы уже доступны для изучения.

        Ссылка на курс: http://your-site.com/courses/{course.id}/

        С уважением,
        Команда образовательной платформы
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

        # Обновляем время последнего обновления курса
        course.updated_at = timezone.now()
        course.save()

        return (
            f"Sent lesson update notifications to {len(recipients)} "
            f"subscribers for course {course.title}"
        )

    except (Course.DoesNotExist, Lesson.DoesNotExist) as e:
        return f"Course or lesson does not exist: {str(e)}"
    except Exception as e:
        return f"Error sending notifications: {str(e)}"


@shared_task
def deactivate_inactive_users():
    """
    Блокировка пользователей, которые не заходили более месяца
    """
    try:
        one_month_ago = timezone.now() - timedelta(days=30)
        inactive_users = User.objects.filter(
            last_login__lt=one_month_ago, is_active=True
        )

        count = inactive_users.count()
        inactive_users.update(is_active=False)

        return f"Deactivated {count} inactive users"

    except Exception as e:
        return f"Error deactivating users: {str(e)}"
