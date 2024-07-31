from aiokafka import AIOKafkaProducer
from pydantic import BaseModel
import json, logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

class NotificationPayload(BaseModel):
    user_email: str
    status: str
    order_id: int


class NotificationService:
    def send_email(self, to_email: str, subject: str, body: str):
        # Implement email sending logic here
        print(f"Sending email to {to_email} with subject '{subject}' and body '{body}'")


async def send_notification(producer: AIOKafkaProducer, 
                            topic: str, 
                            user_message: BaseModel):
    #Before sending to kafka topic
    #Convert Pydantic model to dictionary, 
    # then to JSON string, and finally to bytes
    message_dict = user_message.model_dump()
    json_string = json.dumps(message_dict)
    message_in_bytes = json_string.encode('utf-8')
    await producer.send_and_wait(topic, message_in_bytes)
    logging.info(f'Producer sent message: {message_in_bytes}')

async def notify_order_status(payload: NotificationPayload):
    notification_service = NotificationService()
    notification_service.send_email(
        to_email=payload.user_email,
        subject=f"Order {payload.status}",
        body=f"Your order with ID {payload.order_id} has been {payload.status}."
    )
    logger.info(f"Notification sent successfully for order_id {payload.order_id}")
    return {"message": "Notification sent successfully"}
