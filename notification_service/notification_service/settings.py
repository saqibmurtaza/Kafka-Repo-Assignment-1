import logging
from starlette.config import Config
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:

    config = Config('.env')

    # Load Kafka-related environment variables
    BOOTSTRAP_SERVER = config('BOOTSTRAP_SERVER', cast=str)
    TOPIC_ORDER_STATUS = config('TOPIC_ORDER_STATUS')
    CONSUMER_GROUP_NOTIFYME_MANAGER = config('CONSUMER_GROUP_NOTIFYME_MANAGER', cast=str)

    # Log system-generated messages
    logger.info(f"Loaded BOOTSTRAP_SERVER: {BOOTSTRAP_SERVER} from .env")
    logger.info(f"Loaded TOPIC_ORDER_STATUS: {TOPIC_ORDER_STATUS} from .env")
    logger.info(f"Loaded CONSUMER_GROUP_NOTIFYME_MANAGER: {CONSUMER_GROUP_NOTIFYME_MANAGER} from .env")

    logger.info('Environment variables loaded successfully from .env file')

except Exception as e:
    logger.error(f'FAILED TO LOAD ENVIRONMENT VARIABLES FROM .env file: {e}')
    raise
