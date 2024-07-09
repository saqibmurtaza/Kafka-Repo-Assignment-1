from fastapi import FastAPI
from pydantic import BaseModel
from aiokafka import AIOKafkaConsumer
from notification_service import settings
from .notification_pb2 import NotificationPayloadProto
from notification_service.notifyme_service import NotificationService
import asyncio, logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class NotificationPayload(BaseModel):
    order_id: int
    status: str
    user_email: str
    user_phone: str

@app.post("/notifications/notify/order/status")
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

async def consume_notifications(topic, bootstrap_server, consumer_group_id):
    start_consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        group_id=settings.CONSUMER_GROUP_NOTIFYME_MANAGER
    )
    await start_consumer.start()
    try:
        async for message in start_consumer:
            payload_proto = NotificationPayloadProto()
            payload_proto.ParseFromString(message.value)
            notification_payload = NotificationPayload(
                order_id=payload_proto.order_id,
                status=payload_proto.status,
                user_email=payload_proto.user_email,
                user_phone=payload_proto.user_phone
            )
            await notify_order_status(notification_payload)
            logger.info(f"Consumed and processed message for 
                        order_id {notification_payload.order_id}")
    finally:
        await start_consumer.stop()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_notifications())

@app.get("/")
def read_root():
    return {"message": "Notification Service"}
