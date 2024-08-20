from .model import NotificationPayload
from aiokafka import AIOKafkaProducer
from .order_pb2 import NotificationPayloadProto
from .settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_notification(
        payload: NotificationPayload, 
        producer: AIOKafkaProducer,
        topic: str = settings.TOPIC_USER_EVENTS):
    await producer.start()
    try:
        payload_proto = NotificationPayloadProto(
            order_id=payload.order_id,
            status=payload.status,
            user_email=payload.user_email,
            user_phone=payload.user_phone
        )
        message = payload_proto.SerializeToString()
        await producer.send_and_wait(topic, message)
        logging.info(f"NOTIFICATION_SENT_TO {payload.order_id, payload.user_email}")
    finally:
        await producer.stop()
