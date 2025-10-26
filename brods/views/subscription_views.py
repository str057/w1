from rest_framework import viewsets, permissions
from brods.models import Subscription
from brods.serializers import SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]  # Для тестирования
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.all()
