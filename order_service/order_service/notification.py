from aiokafka import AIOKafkaProducer
from .settings import settings
from .model import NotificationPayload, Order
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
        }
        order_status_message = json.dumps(order_status_payload) #Python object/dict to JSON_string
        await producer.send_and_wait(topic, order_status_message.encode('utf-8'))
        logging.info(
            f"NOTIFICATION_SENT_TO_NOTIFICATION_SERVICE:\n"
            f"ORDER_STATUS: {payload.status}\n"
            f"ORDER_DETAILS:\n"
            f"ITEM: {payload.item_name}\n"
            f"QUANTITY: {payload.quantity}\n"
            f"PRICE: {payload.price}"
        )
    finally:
        await producer.stop()

async def send_user_info_notification(
        payload: NotificationPayload, 
        producer: AIOKafkaProducer,
        topic: str = settings.TOPIC_USER_EVENTS):
    await producer.start()
    try:
        notification_payload = {
            "order_id": payload.order_id,
            "status": payload.status,
            "user_email": payload.user_email,
            "user_phone": payload.user_phone,
        }
        notification_message = json.dumps(notification_payload)  # Convert dict to JSON string
        await producer.send_and_wait(topic, notification_message.encode('utf-8'))
        logging.info(
            f"NOTIFICATION_SENT_TO_NOTIFICATION_SERVICE:\n"
            f"ORDER_ID: {payload.order_id}\n"
            f"USER_EMAIL: {payload.user_email}\n"
            f"USER_PHONE: {payload.user_phone}"
        )
    finally:
        await producer.stop()


