from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import CoursePayment
from ..serializers import CoursePaymentSerializer


class CoursePaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = CoursePaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CoursePayment.objects.filter(user=self.request.user)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CoursePaymentRetrieveView(generics.RetrieveAPIView):
    serializer_class = CoursePaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CoursePayment.objects.filter(user=self.request.user)
