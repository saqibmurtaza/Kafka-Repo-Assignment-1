from pydantic_settings import BaseSettings
from starlette.datastructures import Secret
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    BOOTSTRAP_SERVER: str
    TOPIC_PRODUCTS_CRUD: str
    CONSUMER_GROUP_NOTIFYME_MANAGER: str

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'
        extra = 'allow'

settings = Settings()

logger.info(f"BOOTSTRAP_SERVER: SUCCESSFULLY RETRIEVED")
logger.info(f"TOPIC_PRODUCTS_CRUD: SUCCESSFULLY RETRIEVED")
logger.info(f"DATABASE_URL: SUCCESSFULLY RETRIEVED")

