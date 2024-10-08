from pydantic_settings import BaseSettings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    BOOTSTRAP_SERVER: str
    TOPIC_USER_EVENTS: str
    TOPIC_ORDER_STATUS: str
    TOPIC_NOTIFY_INVENTORY: str
    CONSUMER_GROUP_NOTIFY_MANAGER: str
    NOTIFICATION_SERVICE_URL: str
    
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USER: str
    EMAIL_APP_PASSWORD: str
    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'
        extra = 'allow'

settings = Settings()

logging.info("BOOTSTRAP_SERVER: %s", settings.BOOTSTRAP_SERVER)
logging.info("TOPIC_USER_EVENTS: %s", settings.TOPIC_USER_EVENTS)
logging.info("TOPIC_ORDER_STATUS: %s", settings.TOPIC_ORDER_STATUS)
logging.info("TOPIC_NOTIFY_INVENTORY: %s", settings.TOPIC_NOTIFY_INVENTORY)
logging.info("CONSUMER_GROUP_NOTIFY_MANAGER: %s", settings.CONSUMER_GROUP_NOTIFY_MANAGER)
logging.info("EMAIL_HOST: %s", settings.EMAIL_HOST)
logging.info("EMAIL_PORT: %s", settings.EMAIL_PORT)
logging.info("EMAIL_USER: %s", settings.EMAIL_USER)

