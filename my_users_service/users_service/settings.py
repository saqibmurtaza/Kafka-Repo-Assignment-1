from pydantic_settings import BaseSettings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    BOOTSTRAP_SERVER: str
    TOPIC_USER_EVENTS: str
    CONSUMER_GROUP_NOTIFYME_MANAGER: str
    MOCK_SUPABASE: bool = True
    SUPABASE_URL: str
    SUPABASE_KEY: str


    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'
        extra = 'allow'

settings = Settings()

logger.info(f"BOOTSTRAP_SERVER UPLOAD SUCCESSFULLY")
logger.info(f"TOPIC_USER_EVENTS: UPLOAD SUCCESSFULLY")
logger.info(f"CONSUMER_GROUP_NOTIFYME_MANAGER: UPLOAD SUCCESSFULLY")
