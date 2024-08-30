from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
from .models import UserRegistration, Order, Inventory
from .settings import settings
import smtplib
import json, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#################################################
##### USER_SERVICE_MESSAGE_PROCEESSING_FUNCTION
#################################################
async def process_user_message(message: dict):
    try:
        data = UserRegistration(
            username=message.get("username"),
            email=message.get("email"),
            password=message.get("password"),
            action=message.get("action")
        )
        action = data.action
        access_token = message.get("access_token")  # Extract access token from the message

        if action == "Signup":
            await send_signup_email(data)
        elif action == "Login":
            await send_login_email(data, access_token) # Pass the access token
        elif action == "get_user_profile":
            await send_profile_email(data)
        else:
            logging.warning(f"Unknown action: {action}")
    except json.JSONDecodeError as e:
        logging.error(f"FAILED_TO_DECODE_MESSAGE: {e}")

#################################################
##### ORDER_SERVICE_MESSAGE_PROCEESSING_FUNCTION
#################################################
async def process_order_message(message: dict):
    # New order message processing logic
    try:
        data = Order(
            item_name=message.get("item_name"),
            quantity=message.get("quantity"),
            price=message.get("price"),
            status=message.get("status"),
            user_email=message.get("user_email"),
            user_phone=message.get("user_phone")
        )

        await send_order_email(data)
        
    except json.JSONDecodeError as e:
        logging.error(f"FAILED_TO_DECODE_MESSAGE: {e}")

#################################################
##### ORDER_SERVICE_EMAIL_FUNCTION
#################################################
async def send_order_email(data: Order):
    subject = f"Order {data.status}"
    body = f"Your order for {data.item_name} is now {data.status}."
    await send_email(data.user_email, subject, body)

    logging.info(
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
                f"=====================================================\n"
                f"ORDER_STATUS_MESSAGE_PROCESSED_AND_DISPATCHED_TO_USER\n"
                f"=====================================================\n"
                f"\nPROCESSED_MESSAGE:\n"
                f"\nSTATUS : {data.status}\n"
                f"ITEM_NAME : {data.item_name}\n"
                f"QUANTITY : {data.quantity}\n"
                f"PRICE : {data.price}\n"
                f"USER_EMAIL : {data.user_email}\n"
                f"USER_PHONE : {data.user_phone}\n"
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
            )
#################################################
##### SIGNUP_EMAIL_FUNCTION
#################################################
async def send_signup_email(data: UserRegistration):
    subject = "Welcome to Our Service!"
    body = f"Hello {data.username},\n\nThank you for signing up!"
    await send_email(data.email, subject, body)
    logging.info(
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
                f"=====================================================\n"
                f"SIGN_UP_MESSAGE_DISPATCHED_TO_USER\n"
                f"=====================================================\n"
                f"\nPROCESSED_MESSAGE:\n"
                f"ACTION : {data.action}\n"
                f"USERNAME : {data.username}\n"
                f"EMAIL : {data.email}\n"
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
            )

#################################################
##### LOGIN_EMAIL_FUNCTION
#################################################
async def send_login_email(data: UserRegistration, access_token:str):
    subject = "Login Alert/Generated Token"
    body = body = f"""
    Hello {data.username},

    You have successfully logged in.

    Your access token is: {access_token}

    Best regards,
    Your Service Team
    """
    await send_email(data.email, subject, body)
    logging.info(
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
                f"=====================================================\n"
                f"LOGIN_MESSAGE_&_TOKEN_DISPATCHED_TO_USER\n"
                f"=====================================================\n"
                f"\nPROCESSED_MESSAGE:\n"
                f"ACTION : {data.action}\n"
                f"EMAIL : {data.email}\n"
                f"\nTOKEN : {access_token}\n"
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
            )

#################################################
##### USER_PROFILE_SEND_EMAIL_FUNCTION
#################################################
async def send_profile_email(data: UserRegistration):
    subject = "Profile Accessed"
    body = f"""
    Hello {data.username},\n\n
    Your profile was details:
    {data.username},
    {data.email},
    {data.password}
    
    Thanks.
    ONLINE_SHOPPING_MALL -TEAM
    """
    await send_email(data.email, subject, body)
    logging.info(
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
                f"=====================================================\n"
                f"USER_PROFILE_DISPATCHED_TO_USER\n"
                f"=====================================================\n"
                f"\nPROCESSED_MESSAGE:\n"
                f"ACTION : {data.action}\n"
                f"USERNAME : {data.username}\n"
                f"EMAIL : {data.email}\n"
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
            )
    
#################################################
##### EMAIL_FUNCTIONALITY
#################################################
async def send_email(to_email: str, subject: str, body: str):
    from_email = settings.EMAIL_USER
    password = settings.EMAIL_APP_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server using settings
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls() # Secure the connection using TLS
        server.login(settings.EMAIL_USER, settings.EMAIL_APP_PASSWORD) # Login to the server

        # Send the email
    
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        logging.info(
            f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"    
            f"\n!!!!!!!!!!!!!!!!!!!!!!--EMAIL_SENT_TO {to_email}--!!!!!!!!!!!!!!!!!!!!!!\n"
            f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
        )
      
    except Exception as e:
        logging.error(f"------------FAILED_TO_SEND_EMAIL-------------: {e}")



#################################################
##### INVENTORY_SERVICE_MESSAGE_PROCEESSING_FUNCTION
#################################################

async def process_inventory_message(message: Dict):
    try:
        data = Inventory(
            item_name=message.get("item_name"),
            quantity=message.get("quantity"),
            threshold=message.get("threshold"),
            email=message.get("email")
        )
        if data.quantity <= data.threshold:
            await send_inventory_alert_email(data)
    except json.JSONDecodeError as e:
        logging.error(f"FAILED_TO_DECODE_MESSAGE: {e}")

async def send_inventory_alert_email(data: Inventory):
    subject = "Inventory Alert"
    body = f"""
    Hello,

    The inventory for {data.item_name} is low. Current quantity: {data.quantity}.

    Please restock as soon as possible.

    Best regards,
    Inventory Management Team
    """
    logging.info(f"PREPARING_TO_SEND_INVENTORY_ALERT_EMAIL_TO {data.email} FOR_ITEM {data.item_name}")
    await send_email(data.email, subject, body)
