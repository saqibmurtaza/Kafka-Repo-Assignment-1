from starlette.datastructures import Secret
from starlette.config import Config

env_file = r'F:\kafka_project\.env'

try:
    config = Config(env_file=env_file)

except FileNotFoundError:
    print('Environment variables are not found !')

DATABASE_URL=config("DATABASE_URL", Secret)

# KAFKA
BOOTSTRAP_SERVER=config('BOOTSTRAP_SERVER', str)

KAFKA_TOPIC_MART_PRODUCTS_CRUD=config('KAFKA_TOPIC_MART_PRODUCTS_CRUD', str)
KAFKA_CONSUMER_GROUP_PRODUCT_MANAGER=config('KAFKA_CONSUMER_GROUP_PRODUCT_MANAGER', str)