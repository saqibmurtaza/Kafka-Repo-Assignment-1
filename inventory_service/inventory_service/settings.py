from pydantic_settings import BaseSettings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    BOOTSTRAP_SERVER: str
    TOPIC_INVENTORY_UPDATES: str
    TOPIC_NOTIFY_INVENTORY: str
    CONSUMER_GROUP_INV_MANAGER: str
    CONSUMER_GROUP_NOTIFY_MANAGER: str
    
    SUPABASE_URL: str
    SUPABASE_DB_URL: str
    SUPABASE_KEY: str

    JWT_SECRET: str
    JWT_ALGORITHM: str
    ORDER_KEY: str

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'
        extra = 'allow'

settings = Settings()

logger.info(f"KAFKA_BOOTSTRAP_SERVERS UPLOAD SUCCESSFULLY")
logger.info(f"TOPIC_INVENTORY_UPDATES: UPLOAD SUCCESSFULLY")
logger.info(f"CONSUMER_GROUP_INVENTORY_MANAGER: UPLOAD SUCCESSFULLY")
