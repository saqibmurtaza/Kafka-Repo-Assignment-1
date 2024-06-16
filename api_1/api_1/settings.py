import os
import logging
from starlette.datastructures import Secret
from starlette.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env_file = '/app/.env'

# Check if the .env file exists
if os.path.exists(env_file):
    logger.info('Loading environment variables from %s', env_file)
    config = Config(env_file=env_file)
else:
    logger.warning('Environment variables file not found, using defaults or environment variables if available.')
    config = Config(environ=os.environ)  # Fall back to environment variables if the file is not found

DATABASE_URL=config("DATABASE_URL", Secret)
# KAFKA
BOOTSTRAP_SERVER = config('BOOTSTRAP_SERVER', cast=str, default='default_bootstrap_server')
TOPIC_PRODUCTS_CRUD = config('TOPIC_PRODUCTS_CRUD', cast=str, default='default_topic_products_crud')

logger.info(f"BOOTSTRAP_SERVER: {BOOTSTRAP_SERVER}")
logger.info(f"TOPIC_PRODUCTS_CRUD: {TOPIC_PRODUCTS_CRUD}")
