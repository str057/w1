from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from brods.models import Course, Payment
from brods.serializers import PaymentSerializer


# Временная заглушка StripeService для тестирования
class StripeService:
    @staticmethod
    def create_product(course):
        return type("obj", (object,), {"id": f"prod_{course.id}"})

    @staticmethod
    def create_price(product_id, amount):
        return type("obj", (object,), {"id": f"price_{product_id}"})

    @staticmethod
    def create_checkout_session(
        price_id, course_id, user_email, success_url, cancel_url
    ):
        return type(
            "obj",
            (object,),
            {
                "id": f"cs_test_{course_id}",
                "url": f"https://checkout.stripe.com/test_{course_id}",
                "payment_status": "unpaid",
            },
        )

    @staticmethod
    def retrieve_session(session_id):
        return type(
            "obj",
            (object,),
            {"payment_status": "paid", "payment_intent": f"pi_{session_id}"},
        )


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]  # Для тестирования
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.all()


class CreatePaymentSessionView(APIView):
    permission_classes = [permissions.AllowAny]  # Для тестирования

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

        # Проверяем, не оплачен ли уже курс
        existing_payment = Payment.objects.filter(
            user=request.user if request.user.is_authenticated else None,
            paid_course=course,
            payment_status="paid",
        ).exists()

        if existing_payment:
            return Response(
                {"error": "Этот курс уже оплачен"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Если курс бесплатный
        if course.price == 0:
            # Создаем запись о бесплатной оплате
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

        # Создаем продукт и цену в Stripe если их нет
        if not course.stripe_product_id or not course.stripe_price_id:
            try:
                product = StripeService.create_product(course)
                course.stripe_product_id = product.id

                # Создаем цену (умножаем на 100 для перевода в центы)
                price_amount = int(course.price * 100)
                price = StripeService.create_price(product.id, price_amount)
                course.stripe_price_id = price.id
                course.save()
            except Exception as e:
                return Response(
                    {"error": f"Ошибка создания продукта в Stripe: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Создаем URL для перенаправления
        base_url = request.build_absolute_uri("/")[:-1]  # Убираем trailing slash
        success_url = (
            f"{base_url}/api/payment/success/?session_id={{CHECKOUT_SESSION_ID}}"
        )
        cancel_url = f"{base_url}/api/payment/cancel/"

        try:
            # Создаем сессию оплаты
            session = StripeService.create_checkout_session(
                price_id=course.stripe_price_id,
                course_id=course.id,
                user_email=(
                    request.user.email
                    if request.user.is_authenticated
                    else "test@example.com"
                ),
                success_url=success_url,
                cancel_url=cancel_url,
            )
        except Exception as e:
            return Response(
                {"error": f"Ошибка создания сессии оплаты: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Сохраняем информацию о платеже
        Payment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            paid_course=course,
            amount=course.price,
            payment_method="stripe",
            stripe_session_id=session.id,
        )

        return Response(
            {
                "session_id": session.id,
                "url": session.url,
                "message": "Сессия оплаты создана",
            },
            status=status.HTTP_200_OK,
        )


class PaymentSuccessView(APIView):
    permission_classes = [permissions.AllowAny]  # Для тестирования

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
            # Получаем информацию о сессии
            session = StripeService.retrieve_session(session_id)
        except Exception as e:
            return Response(
                {"error": f"Ошибка получения информации о сессии: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Находим соответствующий платеж
        payment = Payment.objects.filter(
            stripe_session_id=session_id,
            user=request.user if request.user.is_authenticated else None,
        ).first()

        if not payment:
            return Response(
                {"error": "Платеж не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        if session.payment_status == "paid" and payment.payment_status != "paid":
            # Обновляем статус платежа
            payment.payment_status = "paid"
            payment.stripe_payment_intent_id = session.payment_intent
            payment.save()

            return Response(
                {
                    "message": "Оплата прошла успешно! Курс доступен для изучения.",
                    "course_id": payment.paid_course.id,
                    "course_title": payment.paid_course.title,
                },
                status=status.HTTP_200_OK,
            )

        elif payment.payment_status == "paid":
            return Response(
                {
                    "message": "Оплата уже была подтверждена ранее",
                    "course_id": payment.paid_course.id,
                    "course_title": payment.paid_course.title,
                },
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {
                    "message": "Оплата еще не завершена или ожидает обработки",
                    "payment_status": session.payment_status,
                },
                status=status.HTTP_200_OK,
            )


class PaymentCancelView(APIView):
    permission_classes = [permissions.AllowAny]  # Для тестирования

    @extend_schema(
        summary="Отмена оплаты",
        description="Вызывается при отмене оплаты пользователем",
    )
    def get(self, request):
        """Обработка отмены оплаты"""
        return Response(
            {"message": "Оплата отменена. Вы можете попробовать снова."},
            status=status.HTTP_200_OK,
        )


class PaymentHistoryView(APIView):
    permission_classes = [permissions.AllowAny]  # Для тестирования

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
