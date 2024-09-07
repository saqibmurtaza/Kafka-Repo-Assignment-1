from aiokafka import AIOKafkaProducer
from pydantic import BaseModel
from .settings import settings
from .models import UserInfo, UserMessage, LoginInfo
import json, logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

async def notify_user_actions(
        payload: UserInfo,
        producer: AIOKafkaProducer, 
        topic= settings.TOPIC_USER_EVENTS
    ):
    await producer.start()
    try:
        payload_dict = {
            "username": payload.username,
            "email": payload.email,
            "password": payload.password,
            "api_key": payload.api_key,
            "action": payload.action
        }
        message = json.dumps(payload_dict) #Python object/dict to JSON_string
        await producer.send_and_wait(topic, message.encode('utf-8'))
        logging.info(
            f"\n=========================================================\n"
            f"USER_REGISTRATION_DETAILS_SEND_TO_NOTIFICATION_SERVICE:\n"
            f"ACTION: {payload.action}\n"
            f"USERNAME: {payload.username}\n"
            f"USER_EMAIL: {payload.email}\n"
            f"API_KEY: {payload.api_key}\n"
            f"=========================================================\n"
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
            "username": payload.user.username,
            "email": payload.user.email,
            "password": payload.user.password,
            "action": payload.action
        }
        message = json.dumps(payload_dict)  # Convert to JSON string
        await producer.send_and_wait(topic, message.encode('utf-8'))
        logging.info(
            f"\n=========================================================================\n"
            f"\nUSER_PROFILE_NOTIFICATION_SEND_TO_KAFKA:\n"
            f"\nUSERNAME: {payload_dict.get('username')}\n"
            f"PASSWORD: {payload_dict.get('password')}\n" 
            f"USER_EMAIL: {payload_dict.get('email')}\n"  
            f"ACTION: {payload_dict.get('action')}\n"
            f"\n=========================================================================\n"
        )
    finally:
        await producer.stop()
    return None