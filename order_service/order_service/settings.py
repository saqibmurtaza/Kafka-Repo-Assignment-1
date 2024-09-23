from pydantic_settings import BaseSettings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    BOOTSTRAP_SERVER: str
    TOPIC_ORDER_STATUS: str
    TOPIC_PAYMENT_EVENTS: str
    
    MOCK_SUPABASE: bool = True
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_DB_URL:str

    PAYMENT_SERVICE_URL: str

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'
        extra = 'allow'

settings = Settings()


logging.info("BOOTSTRAP_SERVER: %s", settings.BOOTSTRAP_SERVER)
logging.info("TOPIC_ORDER_STATUS: %s", settings.TOPIC_ORDER_STATUS)
logging.info("MOCK_SUPABASE: %s", settings.MOCK_SUPABASE)
logging.info("SUPABASE_URL: %s", settings.SUPABASE_URL)