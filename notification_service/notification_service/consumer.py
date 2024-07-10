from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from pydantic import ValidationError
from notification_service import settings
from .notification_pb2 import NotificationPayloadProto
from notification_service.notifyme_service import NotificationService
from .models import NotificationPayload, UserMessage, User
import asyncio, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_consumer(topics, bootstrap_server, consumer_group_id):
    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers=bootstrap_server,
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
        logger.info(f"Received message: {message}")

        if message.topic == settings.TOPIC_ORDER_STATUS:
            payload_proto = NotificationPayloadProto()
            payload_proto.ParseFromString(message.value)
            
            notification_payload = NotificationPayload(
                order_id=payload_proto.order_id,
                status=payload_proto.status,
                user_email=payload_proto.user_email,
                user_phone=payload_proto.user_phone
            )
            await notify_order_status(notification_payload)
            logger.info(f"Consumed and processed message for order_id {notification_payload.order_id}")

        elif message.topic == settings.TOPIC_USER_EVENTS:
            logger.info("Detected user event message topic.")
            
            try:
                user_message = UserMessage.parse_raw(message.value.decode('utf-8'))
                logger.info(f'USER MESSAGE : {user_message}')
                success = await handle_user_message(user_message)
                if success:
                    logger.info(f"REGISTRATION NOTIFICATION SENT SUCCESSFULLY TO USER {user_message.user.email}")
                else:
                    logger.warning(f"Error sending notification to user {user_message.user.email}")
                    logger.info(f"Consumed and processed user event: {user_message.action} for user {user_message.user.email}")
            except Exception as e:
                logger.error(f"Error processing user message: {e}")

async def notify_order_status(payload: NotificationPayload):
    notification_service = NotificationService()
    notification_service.send_email(
        to_email=payload.user_email,
        subject=f"Order {payload.status}",
        body=f"Your order with ID {payload.order_id} has been {payload.status}."
    )
    notification_service.send_sms(
        to_phone=payload.user_phone,
        message=f"Your order with ID {payload.order_id} has been {payload.status}."
    )
    logger.info(f"Notification sent successfully for order_id {payload.order_id}")
    return {"message": "Notification sent successfully"}


async def handle_user_message(user_message: UserMessage) -> bool:
    notification_service = NotificationService()
    success = False
    if user_message.action == "register":
        # Send an email
        try:
            notification_service.send_email(
                to_email=user_message.user.email,
                subject="Welcome!",
                body=f"Hello {user_message.user.username}, welcome to our service!",
            )
            notification_service.send_sms(
                to_phone=user_message.user.phone,
                message=f"Hello {user_message.user.username}, welcome to our service!",
            )
            success = True
        except Exception as e:
            logger.error(f"ERROR SENDING REGISTRATION NOTIFICATION TO USER {user_message.user.email} : {e}")
    
    elif user_message.action == "login":
        # Send a login notification
        try:
            notification_service.send_email(
                to_email=user_message.user.email,
                subject="Login Notification",
                body=f"Hello {user_message.user.username}, you have successfully logged in!",
            )
            notification_service.send_sms(
                to_phone=user_message.user.phone,
                message=f"Hello {user_message.user.username}, you have successfully logged in!",
            )
            logger.info(f"Notification sent to user {user_message.user.email} for login")
            success = True
        except Exception as e:
            logger.error(f"Error sending notification to user {user_message.user.email} for login: {e}")
    return success