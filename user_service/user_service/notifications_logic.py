from aiokafka import AIOKafkaProducer
from pydantic import BaseModel
import json, logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

class NotificationPayload(BaseModel):
    user_email: str
    status: str
    order_id: int
    action: str


class NotificationService:
    def send_email(self, to_email: str, subject: str, body: str):
        # Implement email sending logic here
        logging.info(f"EMAIL_SEND TO {to_email}; SUBJECT : {subject}; CONTENT : {body}")


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

async def notify_order_status(payload: NotificationPayload):
    notification_service = NotificationService()

    # Customize subject and body based on action
    if payload.action == "registration":
        subject = "Registration Notification"
        body = f"USER {payload.user_email} : REGISTERED_SUCCESSFULLY" 
    
    elif payload.action == "login":
        subject = "Login Notification"
        body = f"USER {payload.user_email} : LOGGED_SUCCESSFULLY"

    elif payload.action == "get_profile":
        subject = "User_Profile Notification"
        body = f"USER {payload.user_email} GOT_PROFILE_SUCCESSFULLY"

    else:
        subject = "User Action Notification"
        body = f"USER {payload.user_email} PERFORMED_ACTION : {payload.status}"

    # Send the email with the customized subject and body
    notification_service.send_email(
        to_email=payload.user_email,
        subject=subject,
        body=body
    )
    return None
