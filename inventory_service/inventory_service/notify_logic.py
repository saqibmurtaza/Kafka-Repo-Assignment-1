from aiokafka import AIOKafkaProducer
from .settings import settings
from .producer import get_kafka_producer
import logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

async def send_message(message,topic,bootstrap_server):
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_server)
    await producer.start()
    try:
        await producer.send_and_wait(topic, message)
    finally:
        await producer.stop()


async def send_batch_inventory_list(message: list):
    async for producer in get_kafka_producer():
        serialized_msgs = [my_inv.SerializeToString() for my_inv in message]
        
        for serialized_msg in serialized_msgs:
            if producer._closed:
                raise RuntimeError("Kafka producer is closed.")
        
            await producer.send_and_wait(settings.TOPIC_NOTIFY_INVENTORY, serialized_msg)
        
        await producer.stop()
        