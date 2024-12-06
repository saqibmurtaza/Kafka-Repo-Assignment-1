from .models import NotifyUser
from .email_function import send_email
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#################################################
##### SIGNUP_EMAIL_FUNCTION
#################################################
async def send_signup_email(data: NotifyUser):
    
    subject = "WELCOME TO ONLINE SHOPPING MALL!"
    body = f'''
    Hello {data.get('username')},

    !***!WELCOME TO ONLINE SHOPPING MALL!***!
    
    Thank you for signing up!
    
    Your Credentials:

    username: {data.get('username')}
    password: {data.get('password')}
    email: {data.get('email')}
    
    Best regards,
    Your Service Team - ONLINE_SHOPPING_MALL
    '''
    await send_email(data['email'], subject, body)
    logging.info(f"Email successfully sent to: {data['email']}")

#################################################
##### LOGIN_EMAIL_FUNCTION
#################################################
async def send_login_email(data: NotifyUser):
    
    subject = "Login Alert"
    body = body = f"""
    Hello {data.get('username')},

    !***!WELCOME TO ONLINE SHOPPING MALL!***!

    You have successfully {data.get('action')} with Credentials:
    username: {data.get('username')}
    password: {data.get('password')}
    Login Token : {data.get('Token')}

    You logged_in with email : {data.get('email')}

    Best regards,
    Your Service Team - ONLINE_SHOPPING_MALL
    """
    await send_email(data['email'], subject, body)
    logging.info(f"Email successfully sent to: {data['email']}")

#################################################
##### USER_PROFILE_SEND_EMAIL_FUNCTION
#################################################
    
async def send_profile_email(payload_list: list[dict]):
    subject = "LIST_OF_PROFILES"
    body = """ ***WELCOME TO ONLINE SHOPPING MALL!*** """
    for my_list in payload_list:

        body += f"""
        ID: {my_list['id']}
        Username: {my_list['username']}
        Role: {my_list['role']}
        Email: {my_list['email']}
        Password: {my_list['password']}
        API Key: {my_list['api_key']}
        Source: {my_list['source']}
        Action: {my_list['action']}
        """
    
    body += """
    Thanks.
    ONLINE SHOPPING MALL - TEAM
    """
    for my_list in payload_list:
        if my_list['role'] == 'admin':
            try:
                await send_email(my_list["email"], subject, body)
                logging.info(f"Email successfully sent to: {my_list['email']}")
            except Exception as e:
                logging.error(f"Failed to send email to {my_list['email']}: {e}")
        else:
            logging.info(f"PROFILES_RECEIVED_BY_ADMINS_ONLY")
    


    