from aiokafka import AIOKafkaProducer
from .order_pb2 import OrderProto as OrderProto 
from .settings import settings
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_order_status_notification(
        orders_list: List[dict],
        producer: AIOKafkaProducer,
        topic: str = settings.TOPIC_ORDER_STATUS
        ):
    
    await producer.start()
    try:
        for order in orders_list:
            # Create the payload from the order fetched from DB
            payload = OrderProto(
                id=order['id'], 
                item_name=order['item_name'],
                quantity=order['quantity'],
                price=order['price'],
                status=order['status'],
                user_email=order['user_email'],
                user_phone=order['user_phone'],
                api_key=order['api_key']
            )

            serialized_payload = payload.SerializeToString()
            await producer.send_and_wait(topic, serialized_payload)
            logging.info(f'SEND_TO_KAFKA : {serialized_payload}')
        
    finally:
        await producer.stop()
