import logging
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel
from aiokafka import AIOKafkaConsumer
from .notification_pb2 import NotificationPayloadProto
from .notifyme_service import NotificationService
from notification_service import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_task = asyncio.create_task(
        consume_notifications(
            topic=settings.TOPIC_ORDER_STATUS,
            bootstrap_servers=settings.BOOTSTRAP_SERVER,
            consumer_group_id=settings.CONSUMER_GROUP_NOTIFYME_MANAGER
        )
    )
    try:
        yield
    except Exception as e:
        logger.error(f"An error occurred in lifespan context manager: {e}")
    finally:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Consumer task cancelled")

app = FastAPI(
    lifespan=lifespan,
    title='Notification Service',
    servers=[
        {
            "url": "http://localhost:8002",
            "description": "Server: Uvicorn, port: 8002"
        }
    ]
)

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
    logger.info(f"Notification sent successfully for order_id {payload.order_id}")
    return {"message": "Notification sent successfully"}

async def consume_notifications(topic, bootstrap_servers, consumer_group_id):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=consumer_group_id
    )
    await consumer.start()
    try:
        async for message in consumer:
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
    except asyncio.CancelledError:
        logger.info("Consumer task cancelled during shutdown")
    finally:
        await consumer.stop()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_notifications(
        topic=settings.TOPIC_ORDER_STATUS,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        consumer_group_id=settings.CONSUMER_GROUP_NOTIFYME_MANAGER
    ))

@app.get("/")
def read_root():
    return {"message": "Notification Service"}
