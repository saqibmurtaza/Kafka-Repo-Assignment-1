from .models import Order
from .email_function import send_email
from .order_pb2 import OrderProto
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#################################################
##### ORDER_SERVICE_MESSAGE_PROCEESSING_FUNCTION
#################################################
async def process_order_message(message: OrderProto ):
    # New order message processing logic
    try:
        data = Order(
            item_name=message.item_name,
            quantity=message.quantity,  
            price=message.price,        
            status=message.status,      
            user_email=message.user_email, 
            user_phone=message.user_phone  
        )

        await send_order_email(data)
        
    except Exception as e:
        logging.error(f"FAILED_TO_DECODE_MESSAGE: {e}")

#################################################
##### ORDER_SERVICE_EMAIL_FUNCTION
#################################################
async def send_order_email(data: Order):
    subject = f"Order {data.status}"
    body = f"Your order for {data.item_name} is now {data.status}."
    await send_email(data.user_email, subject, body)

    logging.info(
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
                f"\nORDER_STATUS_MESSAGE_PROCESSED_AND_DISPATCHED_TO_USER\n"
                f"PROCESSED_MESSAGE:\n"
                f"\nSTATUS : {data.status}\n"
                f"ITEM_NAME : {data.item_name}\n"
                f"QUANTITY : {data.quantity}\n"
                f"PRICE : {data.price}\n"
                f"USER_EMAIL : {data.user_email}\n"
                f"USER_PHONE : {data.user_phone}\n"
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
            )