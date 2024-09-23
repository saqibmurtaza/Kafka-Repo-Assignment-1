from pydantic_settings import BaseSettings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    BOOTSTRAP_SERVER: str
    TOPIC_ORDER_STATUS: str
    CONSUMER_GROUP_PAYMENT_EVENTS: str
    
    MOCK_SUPABASE: bool = True
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_DB_URL:str

    STRIPE_API_KEY: str

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'

settings = Settings()

logger.info("Settings successfully loaded")
