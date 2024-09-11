from .mock_order_service import MockOrderService
from aiokafka.errors import KafkaConnectionError
from order_service import settings
import os, supabase, logging, requests

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

# Singleton instance of MockOrderService
mock_order_instance = MockOrderService()

def get_mock_order_service():  
    return mock_order_instance

def get_real_order_service():
    supabase_url=os.getenv("SUPABASE_URL")
    supabase_key=os.getenv("SUPABASE_KEY")
    return supabase.create_client(supabase_key, supabase_url)

# AUTOMATE KONG CONFIGURATIONS
import requests
import logging

# Create consumer and key in Kong
def create_consumer_and_api_key(id: str, apikey: str):
    try:
        # Create the consumer
        consumer = requests.post(
            'http://kong:8001/consumers',
            data={'username': id}  # Consider using 'username' if email is not valid field
        )
        
        
        
        consumer.raise_for_status()  # Ensure the request was successful
        consumer_id = consumer.json().get('id')

        logging.info(f"CREATED_CONSUMER_WITH_ID: {consumer_id}")

        # Generate API key for the consumer
        consumer_credential = requests.post(
            f'http://kong:8001/consumers/{consumer_id}/key-auth',
            data={'key': apikey}
        )
        consumer_credential.raise_for_status()  # Ensure the request was successful
        return consumer_credential.json()
    
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP_ERROR_OCCURED: {http_err}")
        raise
    except Exception as err:
        logging.error(f"AN_ERROR_OCCURED: {err}")
        raise
