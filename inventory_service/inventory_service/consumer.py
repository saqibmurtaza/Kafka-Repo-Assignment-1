from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from .settings import settings
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_consumer(topic, bootstrap_server, consumer_group_id):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_server,
        group_id=consumer_group_id
    )
    while True:
        try:
            await consumer.start()
            logging.info(f'CONSUMER STARTED .....')
            break
        except KafkaConnectionError as e:
            logging.error(f'CONSUMER STARTUP FAILED {e}, Retry in 5 seconds')
            await asyncio.sleep(5)
    try:
        async for message in consumer:
            logging.info("CONSUMER_RECIEVED_MESSAGE:STATUS:OKAY")
            
    except asyncio.CancelledError:
        logging.info('Consumer Stopped')
    finally:
        await consumer.stop()

