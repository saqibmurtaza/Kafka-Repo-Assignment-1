from .models import Cart
from .email_function import send_email
from .order_pb2 import NotifyOrder
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#################################################
##### ORDER_SERVICE_MESSAGE_PROCEESSING_FUNCTION
#################################################
async def process_order_message(message: NotifyOrder ):
    logging.info(f"ORDER RECD IN PAYLOAD: {message}")
    try:
        # Extract the OrderProto data from the NotifyOrder message
        order_data = message.data
        data = Cart(
            item_name=order_data.item_name,
            description=order_data.description,
            quantity=order_data.quantity,
            price=order_data.price,
            payment_status=order_data.payment_status,
            user_email=order_data.user_email
        )

        await send_order_email(data)
        
    except Exception as e:
        logging.error(f"FAILED_TO_DECODE_MESSAGE: {e}")

#################################################
##### ORDER_SERVICE_EMAIL_FUNCTION
#################################################
async def send_order_email(data: Cart):
    subject = f"ORDER STATUS"
    body = f"""
    YOUR ORDER DETAILS:
    PAYMENT STATUS : {data.payment_status}
    DESCRIPTION: {data.description}
    PRICE: {data.price}
    QUANTITY: {data.quantity}
    USER_EMAIL: {data.user_email}
    """
    await send_email(data.user_email, subject, body)

    logging.info(f"EMAIL_SENT_TO_{data.user_email}")
