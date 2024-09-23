from aiokafka import AIOKafkaProducer
from .order_pb2 import OrderProto as OrderProto 
from .settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_order_status_notification(
        payload: OrderProto,
        producer: AIOKafkaProducer,
        topic:str= settings.TOPIC_ORDER_STATUS
        ):

    await producer.start()
    try:
        payload= OrderProto(
            id = payload.id,
            item_name = payload.item_name,
            quantity = payload.quantity,
            price = payload.price,
            status = payload.status,
            user_email= payload.user_email,
            user_phone = payload.user_phone,
            api_key = payload.api_key
        )

        serialized_payload= payload.SerializeToString()
        
        await producer.send_and_wait(topic, serialized_payload)
        
        logging.info(
            f'\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n'
            f"\nNOTIFICATION_SENT_TO_NOTIFICATION_&_PAYMENT_SERVICE:\n"
            f"\nORDER_STATUS: {payload.status}\n"
            f"ORDER_DETAILS:\n"
            f"ITEM: {payload.item_name}\n"
            f"QUANTITY: {payload.quantity}\n"
            f"PRICE: {payload.price}\n"
            f"USER_EMAIL: {payload.user_email}\n"
            f"USER_PHONE: {payload.user_phone}\n"
            f"AUTHENTICATION_KEY: {payload.api_key}\n"
            f'\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n'
        )
    finally:
        await producer.stop()

