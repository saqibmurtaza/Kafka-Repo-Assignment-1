import os
import logging
from starlette.datastructures import Secret
from starlette.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# env_file_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
env_file_path = './.env'

# Check if the .env file exists
if os.path.exists(env_file_path):
    logger.info('Loading environment variables from %s', env_file_path)
    config = Config(env_file=env_file_path)
else:
    
    logger.warning('No .env file found at %s', env_file_path)
    config = Config(environ=os.environ)  # Fall back to environment variables if the file is not found

DATABASE_URL=config("DATABASE_URL", Secret)
# KAFKA
BOOTSTRAP_SERVER = config('BOOTSTRAP_SERVER', cast=str, default='default_bootstrap_server')
TOPIC_PRODUCTS_CRUD = config('TOPIC_PRODUCTS_CRUD', cast=str, default='default_topic_products_crud')

logger.info(f"BOOTSTRAP_SERVER: {BOOTSTRAP_SERVER}")
logger.info(f"TOPIC_PRODUCTS_CRUD: {TOPIC_PRODUCTS_CRUD}")
