from fastapi import FastAPI
from pydantic import BaseModel
from aiokafka import AIOKafkaConsumer
from notification_service import settings
from .notification_pb2 import NotificationPayloadProto
from notification_service.notifyme_service import NotificationService
import asyncio
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class NotificationPayload(BaseModel):
    order_id: int
    status: str
    user_email: str
    user_phone: str

class User(BaseModel):
    id: int
    username: str
    email: str
    password: str

class UserMessage(BaseModel):
    action: str
    user: User

@app.post("/manual_notifications/notify/order/status")
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
    return {"message": "Notification sent successfully"}

async def consume_notifications(topics, bootstrap_server, consumer_group_id):
    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        group_id=settings.CONSUMER_GROUP_NOTIFYME_MANAGER
    )
    await consumer.start()
    try:
        async for message in consumer:
            if message.topic == 'order_events':
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

            elif message.topic == 'user_events':
                user_message = UserMessage.parse_raw(message.value.decode('utf-8'))
                await handle_user_message(user_message)
                logger.info(f"Consumed and processed user event: {user_message.action} for user {user_message.user.email}")

    finally:
        await consumer.stop()

async def handle_user_message(user_message: UserMessage):
    notification_service = NotificationService()
    if user_message.action == "register":
        # Send a welcome notification
        notification_service.send_email(
            to_email=user_message.user.email,
            subject="Welcome!",
            body=f"Hello {user_message.user.username}, welcome to our service!"
        )
        notification_service.send_sms(
            to_phone=user_message.user.phone,
            message=f"Hello {user_message.user.username}, welcome to our service!"
        )
    elif user_message.action == "login":
        # Send a login notification
        notification_service.send_email(
            to_email=user_message.user.email,
            subject="Login Notification",
            body=f"Hello {user_message.user.username}, you have successfully logged in!"
        )
        notification_service.send_sms(
            to_phone=user_message.user.phone,
            message=f"Hello {user_message.user.username}, you have successfully logged in!"
        )


@app.on_event("startup")
async def startup_event():
    topics = [settings.TOPIC_ORDER_STATUS, settings.TOPIC_USER_EVENTS]
    asyncio.create_task(consume_notifications(
        topics,
        bootstrap_server=settings.BOOTSTRAP_SERVER,
        consumer_group_id=settings.CONSUMER_GROUP_NOTIFYME_MANAGER
    ))


@app.get("/")
def read_root():
    return {"message": "Notification Service"}
