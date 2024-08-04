import asyncio
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from fastapi_1.product_pb2 import ProductEvent
from .settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_consumer(topic, bootstrap_server, consumer_group_id ):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_server,
        group_id=consumer_group_id
    )
    # Retry mechanism to keep up the consumer
    while True:
        try:
            await consumer.start()
            logging.info('CONSUMER STARTED')
            break
        except KafkaConnectionError as e:
            logging.error(f'CONSUMER STARTUP FAILED {e}, Retry in 5 seconds')
            await asyncio.sleep(5)
    try:
            async for msg in consumer:
                product_event = ProductEvent()
                product_event.ParseFromString(msg.value)
                if product_event.operation == "add":
                    product_id = product_event.data.id
                    # Process the received product ID
                    logging.info(f"Received product ID: {product_id}")
                    # You can store this ID or take any other action as required
    finally:
        await consumer.stop()