import logging
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
from .settings import settings
logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVER)
    await producer.start()
   
    try:
        yield producer
        logger.info('Producer Startup ...')
   
    except KafkaConnectionError as e:
        logger.error(f'Producer Startup Error : {e}')
   
    finally:
        await producer.stop()