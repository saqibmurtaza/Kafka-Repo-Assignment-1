from fastapi import HTTPException
from .database import supabase
import requests, json, logging

# AUTOMATE KONG CONFIGURATIONS

# Create consumer and key in Kong
def create_consumer_and_key(username: str, apikey:str):
    try:
       
        # Create consumer
        response = requests.post(
            'http://kong:8001/consumers',
            data={'username': username}
        )
        response.raise_for_status()  # Ensure the request was successful
        consumer_id = response.json().get('id')

        # Generate Consumer_credentials
        response = requests.post(
            f'http://kong:8001/consumers/{consumer_id}/key-auth',
            data={'key': apikey} 
        )
        response.raise_for_status()
        result= response.json()
        return response.json()  # Returns Kong response with API key
    
    except requests.exceptions.RequestException as e:
        logging.error(f"AN_ERROR_OCCURED: {e}")
        raise HTTPException(status_code=409, detail="CONSUMER_ALREADY_EXIST")


def check_kong_consumer(email: str):
    try:

        response= requests.get(f'http://kong:8001/consumers/{email}')
        if response.raise_for_status == 404:
            return None
        response.raise_for_status()
        consumer= response.json()
        consumer_id= consumer.get('id')
        consumer_email= consumer.get('username')

        response= requests.get(f'http://kong:8001/consumers/{consumer_id}/key-auth')
        response.raise_for_status()
        
        consumer_data= response.json().get('data', [])
        for entry in consumer_data:
            if entry.get('consumer', {}).get('id') == consumer_id:
                # extract key
                auth_key = entry.get('key')
                return {
                    'email': consumer_email,
                    'auth_key': auth_key
                }
        return None  # Consumer does not exist

    except requests.exceptions.RequestException as e:
        logging.error(f"NO_CONSUMER_FOUND_WITH_MENTIONED_EMAIL: {e}")
        if e.response and e.response.status_code == 404:
            raise HTTPException(status_code=500, detail="Error checking Kong consumer")
