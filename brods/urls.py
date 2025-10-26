from django.urls import path, include
from rest_framework.routers import DefaultRouter

from brods.views import (
    CourseViewSet,
    LessonViewSet,
    SubscriptionViewSet,
    PaymentViewSet,
    CreatePaymentSessionView,
    PaymentSuccessView,
    PaymentCancelView,
    PaymentHistoryView,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"lessons", LessonViewSet)
router.register(r"subscriptions", SubscriptionViewSet)
router.register(r"course-payments", PaymentViewSet, basename="course-payments")

urlpatterns = [
    path("", include(router.urls)),
    # Payment URLs
    path(
        "payment/course/<int:course_id>/",
        CreatePaymentSessionView.as_view(),
        name="payment-course",
    ),
    path("payment/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("payment/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
    path("payment/history/", PaymentHistoryView.as_view(), name="payment-history"),
]
