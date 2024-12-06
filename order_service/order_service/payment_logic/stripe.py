from ..settings import settings
from stripe import stripe
import logging

logger = logging.getLogger(__name__)


class StripeService:
    def __init__(self, api_key: str):
        stripe.api_key = api_key

    async def process_payment(self, amount: int, currency: str, order_id: int):
        try:
            # Simulate a call to Stripe's API to process the payment
            charge = stripe.Charge.create(
                amount=amount * 100,  # Stripe expects the amount in cents
                currency=currency,
                description=f"Order ID {order_id} payment",
            )
            return charge["status"] == "succeeded"
        except stripe.error.StripeError as e:
            # Log or handle Stripe error
            print(f"Stripe error: {e}")
            return False

