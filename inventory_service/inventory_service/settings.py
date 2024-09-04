from pydantic_settings import BaseSettings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    BOOTSTRAP_SERVER: str
    TOPIC_INVENTORY_UPDATES: str
    MOCK_SUPABASE: bool = True
    SUPABASE_URL: str
    SUPABASE_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str


    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'
        extra = 'allow'

settings = Settings()

logger.info(f"KAFKA_BOOTSTRAP_SERVERS UPLOAD SUCCESSFULLY")
logger.info(f"TOPIC_INVENTORY_UPDATES: UPLOAD SUCCESSFULLY")
logger.info(f"CONSUMER_GROUP_INVENTORY_MANAGER: UPLOAD SUCCESSFULLY")
