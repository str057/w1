import stripe
from django.conf import settings
from brods.models import Course

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    @staticmethod
    def create_product(course: Course):
        """Создание продукта в Stripe"""
        try:
            product = stripe.Product.create(
                name=course.title,
                description=course.description or "Курс без описания",
                metadata={"course_id": str(course.id), "type": "course"},
            )
            return product
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

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
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def create_checkout_session(
        price_id: str,
        course_id: int,
        user_email: str,
        success_url: str,
        cancel_url: str,
    ):
        """Создание сессии для оплаты"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user_email,
                metadata={"course_id": str(course_id), "type": "course_payment"},
                expires_at=None,  # Сессия не истекает
            )
            return session
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def retrieve_session(session_id: str):
        """Получение информации о сессии"""
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def create_payment_intent(amount: int, currency: str = "usd"):
        """Создание Payment Intent (альтернативный способ)"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                automatic_payment_methods={
                    "enabled": True,
                },
            )
            return intent
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
