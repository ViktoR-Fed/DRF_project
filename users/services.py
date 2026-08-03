from decimal import Decimal

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(name, description=None):
    """
    Создание продукта в Stripe
    https://stripe.com/docs/api/products/create
    """
    try:
        product = stripe.Product.create(
            name=name,
            description=description or "",
        )
        return product
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания продукта: {str(e)}")


def create_stripe_price(product_id, amount, currency="usd"):
    """
    Создание цены для продукта в Stripe
    https://stripe.com/docs/api/prices/create
    """
    try:
        if isinstance(amount, (int, float)):
            amount_decimal = Decimal(str(amount))
        else:
            amount_decimal = amount

        # Переводим в копейки/центы (умножаем на 100)
        amount_cents = int(amount_decimal * 100)

        price = stripe.Price.create(
            product=product_id,
            unit_amount=amount_cents,
            currency=currency,
        )
        return price
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания цены: {str(e)}")


def create_stripe_session(price_id, success_url, cancel_url, payment_id=None):
    """
    Создание сессии для оплаты
    https://stripe.com/docs/api/checkout/sessions/create
    """
    try:
        session = stripe.checkout.Session.create(
            ui_mode="hosted",
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "payment_id": str(payment_id) if payment_id else "",
            },
        )
        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания сессии: {str(e)}")


def get_checkout_session(session_id):
    """
    Получение информации о сессии
    https://stripe.com/docs/api/checkout/sessions/retrieve
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка получения сессии: {str(e)}")


def map_stripe_status(stripe_status):
    """
    Маппинг статусов Stripe в статусы приложения
    """
    status_mapping = {
        "open": "pending",  # Ожидает оплаты
        "complete": "paid",  # Оплачено
        "expired": "failed",  # Истекло
        "pending": "pending",  # В процессе
    }
    return status_mapping.get(stripe_status, "pending")
