from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .settings import settings
import smtplib, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#################################################
##### EMAIL_FUNCTIONALITY
#################################################
async def send_email(to_email: str, subject: str, body: str):
    from_email = settings.EMAIL_USER
    password = settings.EMAIL_APP_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server using settings
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        # server.set_debuglevel(1) 
        server.starttls() # Secure the connection using TLS
        server.login(from_email, password) # Login to the server

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
