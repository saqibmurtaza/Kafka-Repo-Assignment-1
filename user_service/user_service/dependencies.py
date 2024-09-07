from fastapi import HTTPException
from .mock_user import MockSupabaseClient
import os, supabase, requests
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client_instance= MockSupabaseClient()

def get_mock_supabase_client():
    return client_instance


def get_supabase_cleint():
    supabase_url= os.getenv("SUPABASE_URL")
    supabase_key= os.getenv("SUPABASE_KEY")
    return supabase.create_client(supabase_url, supabase_key)

def create_consumer_and_key(username: str, apikey:str):
    try:
       
        # Create consumer
        response = requests.post(
            'http://kong:8001/consumers',
            data={'username': username}
        )
        response.raise_for_status()  # Ensure the request was successful
        consumer_id = response.json().get('id')

        # Generate API key
        response = requests.post(
            f'http://kong:8001/consumers/{consumer_id}/key-auth',
            data={'key': apikey} 
        )
        response.raise_for_status()
        return response.json()  # Returns Kong response with API key
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Kong Admin API connection error: {e}")
        raise HTTPException(status_code=502, detail="Unable to connect to Kong Admin API.")
    