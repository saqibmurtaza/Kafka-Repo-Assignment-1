from pydantic_settings import BaseSettings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    BOOTSTRAP_SERVER: str
    TOPIC_PRODUCTS_CRUD: str
    # CONSUMER_GROUP_PRODUCT_MANAGER: str
    CONSUMER_GROUP_NOTIFYME_MANAGER: str
    SUPABASE_URL: str
    SUPABASE_DB_URL: str
    SUPABASE_KEY: str
    
    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'
        extra = 'allow'

settings = Settings()

logger.info(f"BOOTSTRAP_SERVER: SUCCESSFULLY RETRIEVED")
logger.info(f"TOPIC_PRODUCTS_CRUD: SUCCESSFULLY RETRIEVED")
logger.info(f"SUPABASE_URL: SUCCESSFULLY RETRIEVED")

