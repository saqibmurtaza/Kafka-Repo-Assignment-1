from aiokafka import AIOKafkaProducer
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

    # Note: Now we get instance of Notifyuser in payload from main.py, simply convert to dict
    user_dict= payload.dict()
   
    try:
        message = json.dumps(user_dict) # Serialice to JSON_string befor sending to Kafka
        await producer.send_and_wait(topic, message.encode('utf-8'))
        logging.info(
            f"\n!****!****!****!****!****!****!****!****!****!****!****!\n"
            f"USER_ACTIONS_SEND_TO_NOTIFICATION_SERVICE:\n"
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

    action= payload.action  # extract action
    
    users_obj= []
    for my_user in payload.user: # Iterate over each User object, as we get list of objects in payload
        
        users_dict= my_user.dict() # Convert User object to dictionary
        users_dict['action']= action # Add action to the user dictionary
        users_obj.append(users_dict) # Append the user dictionary to the list

    try:
        message = json.dumps(users_obj)  # Convert to JSON string
        # message = json.dumps({"action": "get_user_profile", "user": users_obj})
        await producer.send_and_wait(topic, message.encode('utf-8'))
        logging.info(
            f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
            f"\nPROFILES_SUCCESSFULLY_SENT_TO_NOTIFICATION_SERVICE:"
            f"\nCHECK_EMAIL_IF_YOU_ARE_ADMIN\n"
            f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
        )
    finally:
        await producer.stop()
    return None

