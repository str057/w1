import stripe
from django.conf import settings


class StripeService:
    def __init__(self):
        self.stripe_api_key = settings.STRIPE_SECRET_KEY
        stripe.api_key = self.stripe_api_key

    def create_product(self, course=None, lesson=None):
        """Создание продукта в Stripe"""
        try:
            if course:
                product = stripe.Product.create(
                    name=course.title,
                    description=(
                        course.description[:500]
                        if course.description
                        else f"Курс {course.title}"
                    ),
                )
            elif lesson:
                product = stripe.Product.create(
                    name=lesson.title,
                    description=(
                        lesson.description[:500]
                        if lesson.description
                        else f"Урок {lesson.title}"
                    ),
                )
            return product
        except Exception as e:
            raise Exception(f"Ошибка создания продукта: {str(e)}")

    def create_price(self, product_id, amount):
        """Создание цены в Stripe"""
        try:
            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount,
                currency="rub",
            )
            return price
        except Exception as e:
            raise Exception(f"Ошибка создания цены: {str(e)}")

    def convert_to_cents(self, amount):
        """Конвертация рублей в копейки (центы)"""
        return int(amount * 100)

    def create_checkout_session(self, price_id, success_url, cancel_url, **kwargs):
        """Создание сессии оплаты"""
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
                customer_email=kwargs.get("user_email"),
                metadata=kwargs.get("metadata", {}),
            )
            return session
        except Exception as e:
            raise Exception(f"Ошибка создания сессии оплаты: {str(e)}")

    def retrieve_session(self, session_id):
        """Получение информации о сессии"""
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except Exception as e:
            raise Exception(f"Ошибка получения сессии: {str(e)}")

    def expire_session(self, session_id):
        """Отмена сессии оплаты"""
        try:
            return stripe.checkout.Session.expire(session_id)
        except Exception as e:
            raise Exception(f"Ошибка отмены сессии: {str(e)}")
