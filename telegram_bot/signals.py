from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_course_created_notification


@receiver(post_save)
def generic_handler(sender, instance, created, **kwargs):
    """Generic handler for different models"""
    model_name = sender.__name__


    if model_name == "Course" and created:
        send_course_created_notification.delay(instance.id)


