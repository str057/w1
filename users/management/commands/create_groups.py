import stripe
from django.conf import settings
from brods.models import Course, Lesson

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:

    # === PRODUCT METHODS ===
    @staticmethod
    def create_product(course: Course = None, lesson: Lesson = None):
        """Создание продукта в Stripe для курса или урока"""
        if not course and not lesson:
            raise ValueError("Должен быть указан курс или урок")

        try:
            if course:
                product_data = {
                    "name": course.title,
                    "description": course.description[:500] if course.description else "Курс без описания",
                    "metadata": {
                        "course_id": str(course.id),
                        "type": "course"
                    }
                }
            else:
                product_data = {
                    "name": lesson.title,
                    "description": lesson.description[:500] if lesson.description else "Урок без описания",
                    "metadata": {
                        "lesson_id": str(lesson.id),
                        "course_id": str(lesson.course.id),
                        "type": "lesson"
                    }
                }

            product = stripe.Product.create(**product_data)
            return product

        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка создания продукта: {str(e)}")

    @staticmethod
    def update_product(product_id: str, **kwargs):
        """Обновление продукта в Stripe"""
        try:
            product = stripe.Product.modify(product_id, **kwargs)
            return product
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка обновления продукта: {str(e)}")

    # === PRICE METHODS ===
    @staticmethod
    def create_price(product_id: str, amount: int, currency: str = "usd"):
        """Создание цены в Stripe"""
        try:
            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount,  # Сумма в центах
                currency=currency,
            )
            return price
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка создания цены: {str(e)}")

    @staticmethod
    def update_price(price_id: str, active: bool = None):
        """Обновление цены в Stripe"""
        try:
            update_data = {}
            if active is not None:
                update_data["active"] = active

            price = stripe.Price.modify(price_id, **update_data)
            return price
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка обновления цены: {str(e)}")

    # === CHECKOUT SESSION METHODS ===
    @staticmethod
    def create_checkout_session(
            price_id: str,
            success_url: str,
            cancel_url: str,
            course_id: int = None,
            lesson_id: int = None,
            user_email: str = None,
            metadata: dict = None
    ):
        """Создание сессии для оплаты"""
        if not course_id and not lesson_id:
            raise ValueError("Должен быть указан course_id или lesson_id")

        try:
            session_data = {
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                "mode": "payment",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": metadata or {}
            }

            if user_email:
                session_data["customer_email"] = user_email

            if course_id:
                session_data["metadata"]["course_id"] = str(course_id)
                session_data["metadata"]["type"] = "course_payment"
            elif lesson_id:
                session_data["metadata"]["lesson_id"] = str(lesson_id)
                session_data["metadata"]["type"] = "lesson_payment"

            session = stripe.checkout.Session.create(**session_data)
            return session

        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка создания сессии: {str(e)}")

    # === PAYMENT INTENT METHODS ===
    @staticmethod
    def create_payment_intent(
            amount: int,
            currency: str = "usd",
            metadata: dict = None
    ):
        """Создание Payment Intent (для более гибкого управления платежами)"""
        try:
            intent_data = {
                "amount": amount,
                "currency": currency,
                "automatic_payment_methods": {
                    "enabled": True,
                },
            }

            if metadata:
                intent_data["metadata"] = metadata

            intent = stripe.PaymentIntent.create(**intent_data)
            return intent

        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка создания payment intent: {str(e)}")

    @staticmethod
    def retrieve_payment_intent(intent_id: str):
        """Получение информации о payment intent"""
        try:
            return stripe.PaymentIntent.retrieve(intent_id)
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка получения payment intent: {str(e)}")

    # === SESSION METHODS ===
    @staticmethod
    def retrieve_session(session_id: str):
        """Получение информации о сессии"""
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка получения сессии: {str(e)}")

    @staticmethod
    def expire_session(session_id: str):
        """Завершение сессии"""
        try:
            return stripe.checkout.Session.expire(session_id)
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка завершения сессии: {str(e)}")

    # === WEBHOOK METHODS ===
    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str, webhook_secret: str):
        """Верификация вебхука от Stripe"""
        try:
            return stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            raise Exception(f"Невалидный payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f"Невалидная подпись: {str(e)}")

    # === REFUND METHODS ===
    @staticmethod
    def create_refund(payment_intent_id: str, amount: int = None):
        """Создание возврата средств"""
        try:
            refund_data = {"payment_intent": payment_intent_id}
            if amount:
                refund_data["amount"] = amount

            refund = stripe.Refund.create(**refund_data)
            return refund
        except stripe.error.StripeError as e:
            raise Exception(f"Ошибка создания возврата: {str(e)}")

    # === UTILITY METHODS ===
    @staticmethod
    def convert_to_cents(amount: float) -> int:
        """Конвертация суммы в долларах в центы"""
        return int(amount * 100)

    @staticmethod
    def convert_from_cents(amount: int) -> float:
        """Конвертация суммы из центов в доллары"""
        return amount / 100.0

    @staticmethod
    def format_currency(amount: float, currency: str = "usd") -> str:
        """Форматирование суммы для отображения"""
        if currency.lower() == "usd":
            return f"${amount:.2f}"
        elif currency.lower() == "eur":
            return f"€{amount:.2f}"
        else:
            return f"{amount:.2f} {currency.upper()}"