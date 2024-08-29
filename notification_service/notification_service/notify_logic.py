from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .models import UserRegistration, LoginRequest, UserMessage
from .settings import settings
import smtplib
import json, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_message(message: dict): #received message is payload_dict
    try:
        # Extract Data from payload_dict
        data = UserRegistration(
            username= message.get("username"),
            email= message.get("email"),
            password= message.get("password"),
            action= message.get("action")
        )
        action = data.action

        if action == "Signup":
            await send_signup_email(data)
        elif action == "Login":
            await send_login_email(data)
        elif action == "get_user_profile":
            await send_profile_email(data)
        else:
            logging.warning(f"Unknown action: {action}")
    except json.JSONDecodeError as e:
        logging.error(f"FAILED_TO_DECODE_MESSAGE: {e}")

async def send_signup_email(data: UserRegistration):
    subject = "Welcome to Our Service!"
    body = f"Hello {data.username},\n\nThank you for signing up!"
    logging.info(f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!")
    logging.info(f"PREPARING_TO_SEND_SIGNUP_EMAIL_TO {data.email} FOR_USER {data.username}")
    await send_email(data.email, subject, body)

async def send_login_email(data: UserRegistration):
    subject = "Login Alert"
    body = f"Hello {data.username},\n\nYou have successfully logged in."
    logging.info(f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!")
    logging.info(f"PREPARING_TO_SEND_LOGIN_ALERT_EMAIL_TO {data.email} FOR_USER {data.username}")
    await send_email(data.email, subject, body)

async def send_profile_email(data: UserRegistration):
    subject = "Profile Accessed"
    body = f"Hello {data.username},\n\nYour profile was accessed."
    logging.info(f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!")
    logging.info(f"PREPARING_TO_PROFILE_ACCESSED_EMAIL_TO {data.email} FOR_USER {data.username}")
    await send_email(data.email, subject, body)

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
        logging.info(f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!")
        logging.info(f"\n!!!!!!!!!!!!!!!!!!!!!!--EMAIL_SENT_TO {to_email}--!!!!!!!!!!!!!!!!!!!!!!")
        logging.info(f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!")
    except Exception as e:
        logging.error(f"------------FAILED_TO_SEND_EMAIL-------------: {e}")
