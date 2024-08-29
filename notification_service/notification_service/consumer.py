from aiokafka import AIOKafkaConsumer
from .settings import settings
from .notify_logic import process_user_message, process_order_message
import asyncio, json, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def consume():
    consumer = AIOKafkaConsumer(
        settings.TOPIC_USER_EVENTS,
        settings.TOPIC_ORDER_STATUS,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        group_id=settings.CONSUMER_GROUP_NOTIFY_EVENTS
    )
    await consumer.start()
    try:
        async for msg in consumer:
            # Decode received messages
            logging.info(f"\nRECEIVED_MESSAGE : {msg}\n")
            decoded_msg= msg.value.decode('utf-8') # from bytes to json_formated string
            payload_dict= json.loads(decoded_msg) # from string to dict
   
            if 'username' in payload_dict:
                await process_user_message(payload_dict)
                logging.info(f"------USER_SERVICE_MESSAGES : {payload_dict}")
            elif 'item_name' in payload_dict:
                await process_order_message(payload_dict)
            else:
                logging.warning("Unknown message type received")
    except Exception as e:
        logging.error(f"FAILED_TO_PROCESS_USER_MESSAGE: {e}")

    finally:
        await consumer.stop()

async def start_consumer():
    logging.info('CONSUMER STARTED ---------------------------------------------------------------')
    loop = asyncio.get_event_loop()
    loop.create_task(consume())
