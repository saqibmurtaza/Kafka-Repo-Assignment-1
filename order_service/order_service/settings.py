from pydantic_settings import BaseSettings
from starlette.datastructures import Secret
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

logger.info(f"BOOTSTRAP_SERVER: SUCCESSFULLY RETRIEVED")
logger.info(f"TOPIC_USER_EVENTS: SUCCESSFULLY RETRIEVED")
logger.info(f"MOCK_SUPABASE: {settings.MOCK_SUPABASE}")
logger.info(f"SUPABASE_URL: SUCCESSFULLY RETRIEVED")
logger.info(f"SUPABASE_KEY: SUCCESSFULLY RETRIEVED")
