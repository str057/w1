from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from brods.models import Course, Lesson, Payment
from brods.serializers import PaymentSerializer
from brods.services.stripe_service import StripeService


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.all()


class CreatePaymentSessionView(APIView):
    permission_classes = [permissions.AllowAny]

    def __init__(self):
        super().__init__()
        self.stripe_service = StripeService()

    @extend_schema(
        summary="Создать сессию оплаты для курса",
        description="Создает сессию Stripe для оплаты выбранного курса",
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID курса для оплаты",
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "url": {"type": "string"},
                    "message": {"type": "string"},
                },
            },
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        examples=[
            OpenApiExample(
                "Пример успешного ответа",
                value={
                    "session_id": "cs_test_abc123",
                    "url": "https://checkout.stripe.com/pay/cs_test_abc123",
                    "message": "Сессия оплаты создана",
                },
            )
        ],
    )
    def post(self, request, course_id):
        """Создание сессии оплаты для курса"""
        course = get_object_or_404(Course, id=course_id)

        if request.user.is_authenticated:
            existing_payment = Payment.objects.filter(
                user=request.user,
                paid_course=course,
                payment_status="paid",
            ).exists()

            if existing_payment:
                return Response(
                    {"error": "Этот курс уже оплачен"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if course.price == 0:
            Payment.objects.create(
                user=request.user if request.user.is_authenticated else None,
                paid_course=course,
                amount=0,
                payment_method="transfer",
                payment_status="paid",
            )
            return Response(
                {"message": "Курс бесплатный, доступ открыт"}, status=status.HTTP_200_OK
            )

        if not course.stripe_product_id or not course.stripe_price_id:
            try:
                product = self.stripe_service.create_product(course=course)
                course.stripe_product_id = product.id

                price_amount = self.stripe_service.convert_to_cents(course.price)
                price = self.stripe_service.create_price(product.id, price_amount)
                course.stripe_price_id = price.id
                course.save()
            except Exception as e:
                return Response(
                    {"error": f"Ошибка создания продукта в Stripe: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        base_url = request.build_absolute_uri("/")[:-1]
        success_url = (
            f"{base_url}/api/payment/success/?session_id={{CHECKOUT_SESSION_ID}}"
        )
        cancel_url = f"{base_url}/api/payment/cancel/"

        try:
            session = self.stripe_service.create_checkout_session(
                price_id=course.stripe_price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                course_id=course.id,
                user_email=(
                    request.user.email
                    if request.user.is_authenticated
                    else "test@example.com"
                ),
                metadata={
                    "course_id": str(course.id),
                    "user_id": (
                        str(request.user.id)
                        if request.user.is_authenticated
                        else "anonymous"
                    ),
                },
            )
        except Exception as e:
            return Response(
                {"error": f"Ошибка создания сессии оплаты: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        payment = Payment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            paid_course=course,
            amount=course.price,
            payment_method="stripe",
            stripe_session_id=session.id,
            stripe_price_id=course.stripe_price_id,
            stripe_product_id=course.stripe_product_id,
        )

        return Response(
            {
                "session_id": session.id,
                "url": session.url,
                "message": "Сессия оплаты создана",
                "payment_id": payment.id,
            },
            status=status.HTTP_200_OK,
        )


class CreateLessonPaymentSessionView(APIView):
    permission_classes = [permissions.AllowAny]

    def __init__(self):
        super().__init__()
        self.stripe_service = StripeService()

    @extend_schema(
        summary="Создать сессию оплаты для урока",
        description="Создает сессию Stripe для оплаты выбранного урока",
        parameters=[
            OpenApiParameter(
                name="lesson_id",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID урока для оплаты",
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "url": {"type": "string"},
                    "message": {"type": "string"},
                },
            },
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    )
    def post(self, request, lesson_id):
        """Создание сессии оплаты для урока"""
        lesson = get_object_or_404(Lesson, id=lesson_id)

        if request.user.is_authenticated:
            existing_payment = Payment.objects.filter(
                user=request.user,
                paid_lesson=lesson,
                payment_status="paid",
            ).exists()

            if existing_payment:
                return Response(
                    {"error": "Этот урок уже оплачен"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if lesson.price == 0:
            Payment.objects.create(
                user=request.user if request.user.is_authenticated else None,
                paid_lesson=lesson,
                amount=0,
                payment_method="transfer",
                payment_status="paid",
            )
            return Response(
                {"message": "Урок бесплатный, доступ открыт"}, status=status.HTTP_200_OK
            )

        if not hasattr(lesson, "stripe_product_id") or not lesson.stripe_product_id:
            try:
                product = self.stripe_service.create_product(lesson=lesson)
                lesson.stripe_product_id = product.id

                price_amount = self.stripe_service.convert_to_cents(lesson.price)
                price = self.stripe_service.create_price(product.id, price_amount)
                lesson.stripe_price_id = price.id
                lesson.save()
            except Exception as e:
                return Response(
                    {"error": f"Ошибка создания продукта в Stripe: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        base_url = request.build_absolute_uri("/")[:-1]
        success_url = (
            f"{base_url}/api/payment/success/?session_id={{CHECKOUT_SESSION_ID}}"
        )
        cancel_url = f"{base_url}/api/payment/cancel/"

        try:
            session = self.stripe_service.create_checkout_session(
                price_id=lesson.stripe_price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                lesson_id=lesson.id,
                user_email=(
                    request.user.email
                    if request.user.is_authenticated
                    else "test@example.com"
                ),
                metadata={
                    "lesson_id": str(lesson.id),
                    "user_id": (
                        str(request.user.id)
                        if request.user.is_authenticated
                        else "anonymous"
                    ),
                },
            )
        except Exception as e:
            return Response(
                {"error": f"Ошибка создания сессии оплаты: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        payment = Payment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            paid_lesson=lesson,
            amount=lesson.price,
            payment_method="stripe",
            stripe_session_id=session.id,
            stripe_price_id=lesson.stripe_price_id,
            stripe_product_id=lesson.stripe_product_id,
        )

        return Response(
            {
                "session_id": session.id,
                "url": session.url,
                "message": "Сессия оплаты для урока создана",
                "payment_id": payment.id,
            },
            status=status.HTTP_200_OK,
        )


class PaymentSuccessView(APIView):
    permission_classes = [permissions.AllowAny]

    def __init__(self):
        super().__init__()
        self.stripe_service = StripeService()

    @extend_schema(
        summary="Обработка успешной оплаты",
        description="Проверяет статус оплаты и обновляет статус платежа",
        parameters=[
            OpenApiParameter(
                name="session_id",
                type=str,
                location=OpenApiParameter.QUERY,
                description="ID сессии Stripe",
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "course_id": {"type": "integer"},
                    "course_title": {"type": "string"},
                    "lesson_id": {"type": "integer"},
                    "lesson_title": {"type": "string"},
                },
            }
        },
    )
    def get(self, request):
        """Обработка успешной оплаты"""
        session_id = request.GET.get("session_id")

        if not session_id:
            return Response(
                {"error": "Session ID не предоставлен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = self.stripe_service.retrieve_session(session_id)
        except Exception as e:
            return Response(
                {"error": f"Ошибка получения информации о сессии: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.filter(
            stripe_session_id=session_id,
        ).first()

        if not payment:
            return Response(
                {"error": "Платеж не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        if session.payment_status == "paid" and payment.payment_status != "paid":
            payment.payment_status = "paid"
            payment.stripe_payment_intent_id = session.payment_intent
            payment.payment_date = timezone.now()
            payment.save()

            response_data = {
                "message": "Оплата прошла успешно! Материал доступен для изучения.",
            }

            if payment.paid_course:
                response_data.update(
                    {
                        "course_id": payment.paid_course.id,
                        "course_title": payment.paid_course.title,
                    }
                )
            elif payment.paid_lesson:
                response_data.update(
                    {
                        "lesson_id": payment.paid_lesson.id,
                        "lesson_title": payment.paid_lesson.title,
                    }
                )

            return Response(response_data, status=status.HTTP_200_OK)

        elif payment.payment_status == "paid":
            response_data = {
                "message": "Оплата уже была подтверждена ранее",
            }

            if payment.paid_course:
                response_data.update(
                    {
                        "course_id": payment.paid_course.id,
                        "course_title": payment.paid_course.title,
                    }
                )
            elif payment.paid_lesson:
                response_data.update(
                    {
                        "lesson_id": payment.paid_lesson.id,
                        "lesson_title": payment.paid_lesson.title,
                    }
                )

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            return Response(
                {
                    "message": "Оплата еще не завершена или ожидает обработки",
                    "payment_status": session.payment_status,
                },
                status=status.HTTP_200_OK,
            )


class PaymentCancelView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Отмена оплаты",
        description="Вызывается при отмене оплаты пользователем",
    )
    def get(self, request):
        """Обработка отмены оплаты"""
        session_id = request.GET.get("session_id")

        if session_id:
            Payment.objects.filter(
                stripe_session_id=session_id, payment_status="pending"
            ).update(payment_status="canceled")

        return Response(
            {"message": "Оплата отменена. Вы можете попробовать снова."},
            status=status.HTTP_200_OK,
        )


class PaymentHistoryView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="История платежей пользователя",
        description="Возвращает историю всех платежей текущего пользователя",
        responses=PaymentSerializer(many=True),
    )
    def get(self, request):
        """Получение истории платежей пользователя"""
        if request.user.is_authenticated:
            payments = Payment.objects.filter(user=request.user).order_by(
                "-payment_date"
            )
        else:
            payments = Payment.objects.all().order_by("-payment_date")

        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Детали платежа",
        description="Возвращает детальную информацию о конкретном платеже",
        parameters=[
            OpenApiParameter(
                name="payment_id",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID платежа",
            )
        ],
        responses=PaymentSerializer,
    )
    def get(self, request, payment_id):
        """Получение деталей платежа"""
        payment = get_object_or_404(Payment, id=payment_id)

        if request.user.is_authenticated and payment.user != request.user:
            return Response(
                {"error": "У вас нет доступа к этому платежу"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExpirePaymentSessionView(APIView):
    permission_classes = [permissions.AllowAny]

    def __init__(self):
        super().__init__()
        self.stripe_service = StripeService()

    @extend_schema(
        summary="Отменить сессию оплаты",
        description="Отменяет активную сессию оплаты в Stripe",
        parameters=[
            OpenApiParameter(
                name="session_id",
                type=str,
                location=OpenApiParameter.QUERY,
                description="ID сессии Stripe для отмены",
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                },
            }
        },
    )
    def post(self, request):
        """Отмена сессии оплаты"""
        session_id = request.GET.get("session_id")

        if not session_id:
            return Response(
                {"error": "Session ID не предоставлен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.filter(stripe_session_id=session_id).first()
            if not payment:
                return Response(
                    {"error": "Платеж не найден"}, status=status.HTTP_404_NOT_FOUND
                )

            self.stripe_service.expire_session(session_id)

            payment.payment_status = "canceled"
            payment.save()

            return Response(
                {"message": "Сессия оплаты отменена"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Ошибка при отмене сессии: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
