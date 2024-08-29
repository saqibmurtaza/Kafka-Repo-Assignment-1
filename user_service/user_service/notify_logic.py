from aiokafka import AIOKafkaProducer
from pydantic import BaseModel
from .settings import settings
from .models import UserRegistration, Token, UserMessage, LoginRequest, ActionEnum, UserListResponse
import json, logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

async def notify_user_registration(
        payload: UserRegistration,
        producer: AIOKafkaProducer, 
        topic= settings.TOPIC_USER_EVENTS
    ):
    await producer.start()
    try:
        payload_dict = {
            "username": payload.username,
            "email": payload.email,
            "password": payload.password,
            "action": payload.action
        }
        message = json.dumps(payload_dict) #Python object/dict to JSON_string
        await producer.send_and_wait(topic, message.encode('utf-8'))
        logging.info(
            f"\n=========================================================\n"
            f"USER_REGISTRATION_DETAILS_SEND_TO_NOTIFICATION_SERVICE:\n"
            f"USERNAME: {payload.username}\n"
            f"USER_EMAIL: {payload.email}\n"
            f"ACTION: {payload.action}\n"
            f"=========================================================\n"
        )
    finally:
        await producer.stop()
    return None

async def send_token(
        token_payload: Token,
        message_payload: LoginRequest, 
        producer: AIOKafkaProducer, 
        topic= settings.TOPIC_USER_EVENTS   
    ):
    await producer.start()
    try:
        # Prepare the combined payload dictionary
        combined_payload_dict = {
            "access_token": token_payload.access_token,
            "username": message_payload.username,
            "email": message_payload.email,
            "password": message_payload.password,
            "action": message_payload.action
        }
        
        # Convert the combined dictionary to a JSON string
        message_combined = json.dumps(combined_payload_dict)
        
        # Send the message to Kafka
        await producer.send_and_wait(topic, message_combined.encode('utf-8'))

        logging.info(
            f"\n=========================================================================\n"
            f"\n********************TOKEN_SEND_TO_NOTIFICATION_SERVICE:********************\n"
            f"\nTOKEN: {combined_payload_dict['access_token']}\n"
            f"\nemail: {combined_payload_dict['email']}\n"
            f"action: {combined_payload_dict['action']}\n"
            f"\n===========================================================================\n"
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
