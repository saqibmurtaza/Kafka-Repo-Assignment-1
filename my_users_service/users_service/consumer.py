from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from pydantic import ValidationError
from users_service import settings
from .models import UserMessage
import asyncio, logging, json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_consumer(topics, bootstrap_server, consumer_group_id):
    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers='broker:9092',
        group_id=consumer_group_id
    )
    while True:
        try:
            await consumer.start()
            logging.info("CONSUMER STARTED SUCCESSFULLY ....")
            break
        except KafkaConnectionError as e:
            logging.error(f'CONSUMER STARTUP FAILED {e}, Retry in 5 seconds')
            await asyncio.sleep(5)
    
    async for message in consumer:
        logger.info(f"Received message: {message.value}")

        if message.topic == settings.TOPIC_USER_EVENTS:
            try:
                # Deserialize JSON string to dictionary
                message_dict = json.loads(message.value)
                # Parse dictionary to Pydantic model using model_validate
                user_message = UserMessage.model_validate(message_dict)
                # Convert Pydantic model to dictionary
                user_message_dict = user_message.model_dump()
            except Exception as e:
                logger.error(f"Error processing user message: {e}")

