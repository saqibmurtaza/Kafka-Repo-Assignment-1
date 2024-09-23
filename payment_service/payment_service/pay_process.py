from .settings import settings
from .order_pb2 import OrderProto as OrderProto
import logging, stripe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_payment(payload: OrderProto):
    # Extract_Details
    order_id = payload.id
    price = payload.price
    currency = 'usd'
    # Use a Stripe test token for card payments
    payment_method_id = "pm_card_visa"  # Stripe's predefined test token for Visa
    
    #  Call payment gateways (e.g.Stripe)
    payment_status = await initiate_payment(
            order_id, 
            price, 
            currency, 
            payment_method_id
            )
    # Prepare status message
    status_message = "CONFIRMED" if payment_status == "SUCCESS" else "FAILED"
    
    logging.info(
        f'*************************\nPAYMENT_STATUS : {status_message}\n'
        f'PAID_AMOUNT $ : {price}\n*************************\n'
        )
    return status_message

# Set your Stripe API key
stripe.api_key = settings.STRIPE_API_KEY

async def initiate_payment(order_id, amount, currency, payment_method_id):
    try:
        amount_in_cents=int(amount * 100)
        # Create a payment intent with Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,  # Stripe expects the amount in the smallest currency unit (e.g., cents for USD)
            currency=currency,
            payment_method=payment_method_id,
            description=f"Payment for order {order_id}",
            confirm=True,  # Automatically confirm the payment
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": 'never'  # Disallow redirects
            }
        )
        
        if payment_intent['status'] == 'succeeded':
            return "SUCCESS"
        else:
            return "FAILED"
    except stripe.error.CardError as e:
        logging.error(f"*********CARD_ERROR: {e}")
        return "FAILED"
    except Exception as e:
        logging.error(f"PAYMENT_FAILED**************: {e}")
        return "FAILED"

