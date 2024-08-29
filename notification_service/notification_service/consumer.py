from aiokafka import AIOKafkaConsumer
from .settings import settings
from .notify_logic import process_message
from .models import UserRegistration
import asyncio, json, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def consume():
    consumer = AIOKafkaConsumer(
        settings.TOPIC_USER_EVENTS,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        group_id=settings.CONSUMER_GROUP_NOTIFY_EVENTS
    )
    await consumer.start()
    try:
        async for msg in consumer:
            # Decode received messages
            decoded_msg= msg.value.decode('utf-8') # from bytes to json_formated string
            payload_dict= json.loads(decoded_msg) # from string to dict
            logging.info(f"DECODED_MESSAGE : {payload_dict}")
            await process_message(payload_dict)
    finally:
        await consumer.stop()

async def start_consumer():
    logging.info('CONSUMER STARTED ---------------------------------------------------------------')
    loop = asyncio.get_event_loop()
    loop.create_task(consume())
