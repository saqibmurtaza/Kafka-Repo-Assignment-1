from .models import UserRegistration
from .email_function import send_email
import logging, json

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

        if action == "Signup":
            await send_signup_email(data)
        elif action == "Login":
            await send_login_email(data)
        elif action == "get_user_profile":
            # Create a dictionary from the UserRegistration object for sending the profile email
            payload_dict = {
                'username': data.username,
                'email': data.email,
                'password': data.password,
                'api_key': message.get('api_key'),  # Assuming these are in the incoming message
                'source': message.get('source'),  # Assuming these are in the incoming message
                'action': data.action
            }
            await send_profile_email(payload_dict)
    
        else:
            logging.warning(f"Unknown action: {action}")
    except json.JSONDecodeError as e:
        logging.error(f"FAILED_TO_DECODE_MESSAGE: {e}")

#################################################
##### SIGNUP_EMAIL_FUNCTION
#################################################
async def send_signup_email(data: UserRegistration):
    subject = "WELCOME TO ONLINE SHOPPING MALL!"
    body = f'''
    Hello {data.username},

    !***!WELCOME TO ONLINE SHOPPING MALL!***!
    
    Thank you for signing up!
    
    Your Credentials:

    username: {data.username}
    password: {data.password}
    email: {data.email}
    
    Best regards,
    Your Service Team - ONLINE_SHOPPING_MALL
    '''
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
async def send_login_email(data: UserRegistration):
    subject = "Login Alert"
    body = body = f"""
    Hello {data.username},

    !***!WELCOME TO ONLINE SHOPPING MALL!***!

    You have successfully {data.action} with Credentials:
    username: {data.username}
    password: {data.password}

    Best regards,
    Your Service Team - ONLINE_SHOPPING_MALL
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
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
            )

#################################################
##### USER_PROFILE_SEND_EMAIL_FUNCTION
#################################################
async def send_profile_email(payload_dict: dict):
    subject = "Profile Accessed"
    body = f"""
    !***!WELCOME TO ONLINE SHOPPING MALL!***!
    
    Hello {payload_dict['username']},\n\n
    Your profile details:\n
    action: {payload_dict['action']}
    Username: {payload_dict['username']}\n
    Email: {payload_dict['email']}\n
    Password: {payload_dict['password']}\n
    API Key: {payload_dict['api_key']}\n
    Source: {payload_dict['source']}\n
    
    Thanks.
    ONLINE_SHOPPING_MALL - TEAM
    """
    await send_email(payload_dict["email"], subject, body)
    
    # Log the message after sending
    logging.info(
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
                f"=====================================================\n"
                f"USER_PROFILE_DISPATCHED_TO_USER\n"
                f"=====================================================\n"
                f"\nPROCESSED_MESSAGE:\n"
                f"ACTION : {payload_dict['action']}\n"  # Use payload_dict here
                f"USERNAME : {payload_dict['username']}\n"
                f"EMAIL : {payload_dict['email']}\n"
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
            )
    