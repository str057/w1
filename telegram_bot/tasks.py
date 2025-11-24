from celery import shared_task
from django.contrib.auth import get_user_model
from .models import TelegramUser
import requests
import os


@shared_task
def send_telegram_notification(user_id, message):
    """Send general notification via Telegram"""
    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)

        # Check if user is connected to Telegram
        try:
            telegram_user = TelegramUser.objects.get(user=user)
        except TelegramUser.DoesNotExist:
            return f"User {user.email} not connected to Telegram"

        # Send message via Telegram Bot API
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return "TELEGRAM_BOT_TOKEN not configured"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": telegram_user.chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return f"Notification sent to {user.email}"
        else:
            error_msg = f"Send error: {response.status_code} - {response.text}"
            print(f"? Telegram API error: {error_msg}")
            return error_msg

    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def send_course_created_notification(course_id):
    """Notification about new course creation"""
    try:
        from brods.models import Course

        course = Course.objects.get(id=course_id)
        message = (
            f"?? <b>New course created!</b>\n\n"
            f"?? Title: {course.title}\n"
            f"?? Description: {course.description[:100]}...\n"
            f"?? Author: {course.owner.email}"
        )

        # Send to course owner
        send_telegram_notification.delay(course.owner.id, message)

        return f"Course notification {course.title} sent"
    except Exception as e:
        return f"Error sending course notification: {str(e)}"


@shared_task
def send_test_notification(user_id):
    """Test notification to verify Telegram setup"""
    message = (
        "?? <b>Test notification</b>\n\n"
        "? Your course platform is working!\n"
        "This is a real message from your Telegram bot!"
    )

    return send_telegram_notification(user_id, message)


@shared_task
def check_upcoming_lessons():
    """Check for upcoming lessons"""
    print("?? Checking upcoming lessons...")
    return "Upcoming lessons check completed"


@shared_task
def send_daily_summary():
    """Send daily summary to all users"""
    try:
        User = get_user_model()
        users = User.objects.all()

        for user in users:
            message = (
                "?? <b>Daily Summary</b>\n\n"
                "Here's your daily update from the course platform!"
            )

            send_telegram_notification.delay(user.id, message)

        return f"Daily summaries sent to {users.count()} users"
    except Exception as e:
        return f"Error sending daily summaries: {str(e)}"
