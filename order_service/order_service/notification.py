from aiokafka import AIOKafkaProducer
from .settings import settings
from .model import Order
import json, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_order_status_notification(
        payload: Order, 
        producer: AIOKafkaProducer,
        topic: str = settings.TOPIC_ORDER_STATUS):
    await producer.start()
    try:
        order_status_payload = {
            "item_name": payload.item_name,
            "quantity": payload.quantity,
            "price": payload.price,
            "status": payload.status,
            "user_email": payload.user_email,
            "user_phone": payload.user_phone
        }
        order_status_message = json.dumps(order_status_payload) #Python object/dict to JSON_string
        await producer.send_and_wait(topic, order_status_message.encode('utf-8'))
        logging.info(
            f"NOTIFICATION_SENT_TO_NOTIFICATION_SERVICE:\n"
            f"ORDER_STATUS: {payload.status}\n"
            f"ORDER_DETAILS:\n"
            f"ITEM: {payload.item_name}\n"
            f"QUANTITY: {payload.quantity}\n"
            f"PRICE: {payload.price}\n"
            f"USER_EMAIL: {payload.user_email}\n"
            f"USER_PHONE: {payload.user_phone}\n"
        )
    finally:
        await producer.stop()

