from pydantic_settings import BaseSettings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    BOOTSTRAP_SERVER: str
    TOPIC_PAYMENT_EVENTS: str
    PAYFAST_MERCHANT_ID: str
    PAYFAST_MERCHANT_KEY: str
    PAYFAST_PASSPHRASE: str
    STRIPE_API_KEY: str

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'

settings = Settings()

logger.info("Settings successfully loaded")
