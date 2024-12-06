from aiokafka import AIOKafkaProducer
from .order_pb2 import NotifyOrder, OrderProto
from .settings import settings
from typing import List, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_order_status_notification(
        orders_list: Union[List[dict], dict],
        producer: AIOKafkaProducer,
        topic: str = settings.TOPIC_ORDER_STATUS
        ):
    
    order_recd= NotifyOrder() # First create instance of protobuf_object
    order_recd.ParseFromString(orders_list) # Deserialize into a Protobuf_message_object

    await producer.start()
    try:
        order_recd = order_recd if isinstance(order_recd, list) else [order_recd]
        for my_order in order_recd:
            # Create the payload from the Protobuf message
            payload = NotifyOrder(
                action=my_order.action,
                data=OrderProto(  # Populate the nested Protobuf message
                    id=my_order.data.id,
                    item_name=my_order.data.item_name,
                    description=my_order.data.description,
                    quantity=my_order.data.quantity,
                    price=my_order.data.price,
                    payment_status=my_order.data.payment_status,
                    user_email=my_order.data.user_email
                )
            )

            serialized_payload = payload.SerializeToString()
            await producer.send_and_wait(topic, serialized_payload)
            logging.info(f'ORDER_STATUS_SEND__TO_NOTIFICATION_SERVICE')
        
    finally:
        await producer.stop()
    
async def send_batch_notifications(
        notify_orders, 
        producer: AIOKafkaProducer,
        topic: str = settings.TOPIC_ORDER_STATUS
        
        ):
    serialized_msgs = [order.SerializeToString() for order in notify_orders]
    for serialized_msg in serialized_msgs:
        if producer._closed:
            raise RuntimeError("Kafka producer is closed.")
        await producer.send_and_wait(topic, serialized_msg)

