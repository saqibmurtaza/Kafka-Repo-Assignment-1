from .order_pb2 import OrderProto
from .settings import settings
import logging, requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API CALL TO ORDER_SERVICE
async def notify_order_service(order_id, payment_status):
    url = "http://order_service:8010/orders/order_status"
    payload = {
        "order_id": order_id,
        "status": payment_status
    }

    try: 
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logging.error(f"ERROR_NOTIFYING_ORDER_SERVICE: {e}")
        return None
    
# NOTIFY_TO_ORDER_SERVICE
async def handle_notifications(order_message: OrderProto, status_message: str):
    order_id = order_message.id
    price = order_message.price
    currency = 'usd'

    await notify_order_service(order_id, status_message) # API_Call_To_Order_service

    logging.info(
        f'*************************\nMESSAGE_SENT_TO_ORDER_SERVICE:\n'
        f'PAYMENT_STATUS : {status_message}\n'
        f'ORDER_ID : {order_id}\n'
        f'AMOUNT : {price}\n'
        f'CURRENCY : {currency}\n*************************\n'
    )
    return None
