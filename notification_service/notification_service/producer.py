from aiokafka import AIOKafkaProducer
from .settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

# Initialize the Kafka producer once
async def init_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVER)
    await producer.start()
    return producer

# Close the producer
async def close_producer(producer: AIOKafkaProducer):
    await producer.stop()

