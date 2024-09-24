from .mock_order import MockOrderService
import os, supabase, logging, httpx

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

# Create consumer and key in Kong
async def create_consumer_and_api_key(email: str, apikey: str):
    try:
        # First, check if the consumer already exists
        consumer_response = await httpx.get(f"http://kong:8001/consumers/{email}")
        
        if consumer_response.status_code == 200:
            # Consumer exists, so we don't need to create it again
            return await consumer_response.json()

        # # If consumer doesn't exist, try creating it
        consumer = await httpx.post(
            'http://kong:8001/consumers',
            data={'username': email}  # Consider using 'username' if email is not valid field
        )
        
        consumer.raise_for_status()  # Ensure the request was successful
        consumer_username = await consumer.json().get('username')

        logging.info(f"CREATED_CONSUMER_WITH_EMAIL: {consumer_username}")

        # Generate API key for the consumer
        consumer_credential = await httpx.post(
            f'http://kong:8001/consumers/{consumer_username}/key-auth',
            data={'key': apikey}
        )
        consumer_credential.raise_for_status()  # Ensure the request was successful
        return consumer_credential.json()
    
    except Exception as err:
        logging.info(f"CONSUMER_FOR {email} ALREADY_EXIST, PROCEEDING_WITHOUT_CREATION")
        logging.error(f"AN_ERROR_OCCURED: {err}")
        