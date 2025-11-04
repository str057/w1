from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """Handle incoming Telegram messages"""
    try:
        data = json.loads(request.body)

        # Extract message info
        message = data.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        username = message.get("from", {}).get("username", "")
        first_name = message.get("from", {}).get("first_name", "")

        if chat_id and text:
            print(f"?? Received message from {username} ({first_name}): {text}")
            print(f"?? Chat ID: {chat_id}")

            # You can save this chat_id to user profile
            # or respond to specific commands

            return JsonResponse({"status": "ok"})

        return JsonResponse({"status": "no message"})

    except Exception as e:
        print(f"? Webhook error: {e}")
        return JsonResponse({"status": "error"}, status=500)
