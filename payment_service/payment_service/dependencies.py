from .services.payfast import PayFastService
from .services.stripe import StripeService
from .settings import settings

def get_payfast_service():
    return PayFastService(
        merchant_id=settings.PAYFAST_MERCHANT_ID,
        merchant_key=settings.PAYFAST_MERCHANT_KEY,
        passphrase=settings.PAYFAST_PASSPHRASE
    )

def get_stripe_service():
    return StripeService(api_key=settings.STRIPE_API_KEY)
