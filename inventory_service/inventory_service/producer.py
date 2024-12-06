from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
from inventory_service.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVER)
    await producer.start()
    try:
        yield producer
        logging.info('Producer Startup ...')
    except KafkaConnectionError as e:
        logging.error(f'Producer Startup Error : {e}')
    finally:
        await producer.stop()

async def send_message(message,topic,bootstrap_server):
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_server)
    await producer.start()
    try:
        await producer.send_and_wait(topic, message)
    finally:
        await producer.stop()