from aiokafka import AIOKafkaProducer
from pydantic import BaseModel
from .settings import settings
from .models import UserMessage, NotifyUser, User
import json, logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

async def notify_user_actions(
        payload: NotifyUser,
        producer: AIOKafkaProducer, 
        topic= settings.TOPIC_USER_EVENTS
    ):
    await producer.start()
    # Prepary Dict before serialization to string
    user_data = {
            "action": payload.get('action'),
            "id": payload.get('id'),
            "username": payload.get('username'),
            "email": payload.get('email'),
            "password": payload.get('password'),
            "source": "mock"
        }

    try:
        message = json.dumps(user_data) #json.dumps to JSON_string
        await producer.send_and_wait(topic, message.encode('utf-8'))
        logging.info(
            f"\n!****!****!****!****!****!****!****!****!****!****!****!\n"
            f"USER_ACTION_DETAILS_SEND_TO_NOTIFICATION_SERVICE:\n"
            f"DETAILS\n"
            f"{message}\n"
            f"\n!****!****!****!****!****!****!****!****!****!****!****!\n"
        )
    finally:
        await producer.stop()
    return None


async def notify_user_profile(
        payload: UserMessage,
        producer: AIOKafkaProducer,
        topic= settings.TOPIC_USER_EVENTS
    ):
    await producer.start()
    try:
        payload_dict = {
            "action": payload.action,
            "id": payload.user.id,
            "username": payload.user.username,
            "email": payload.user.email,
            "password": payload.user.password,
            "api_key": payload.user.api_key,
            "source": payload.user.source
            
        }
        message = json.dumps(payload_dict)  # Convert to JSON string
        await producer.send_and_wait(topic, message.encode('utf-8'))
        logging.info(
            f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
            f"\nUSER_PROFILE_NOTIFICATION_SUCCESSFULLY_SENT_TO_NOTIFICATION_SERVICE:\n"
            f"\nUSER_ID: {payload_dict.get('id')}\n" 
            f"USERNAME: {payload_dict.get('username')}\n" 
            f"USER_EMAIL: {payload_dict.get('email')}\n"
            f"PASSWORD: FIND_YOUR_ PASSWORD_& API_KEY_IN_YOUR_REGISTERED_EMAIL\n"  
            f"AUTH_KEY: {payload_dict.get('api_key')}\n"
            f"SOURCE: {payload_dict.get('source')}\n"
            f"ACTION: get_user_profile\n"
            f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
        )
    finally:
        await producer.stop()
    return None

