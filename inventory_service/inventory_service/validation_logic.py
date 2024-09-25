from fastapi import HTTPException
import httpx, requests
import logging

def validate_api_key(apikey:str, email:str):
    try:
        response = requests.get(
            "http://user_service:8009/user/profile", 
            headers={
                "apikey": apikey,
                "email": email
                },
            timeout=10
        )

        response.raise_for_status()
        response_json = response.json()
    
        if isinstance(response_json, dict) and 'user' in response_json:
            return response_json.get("user")  # Return user data if present

        # Handle invalid API key
        raise HTTPException(status_code=403, detail="INVALID_API_KEY")

    except requests.ConnectionError:
        logging.error('CONNECTION_REFUSED_TO_USER_SERVICE')
        raise HTTPException(status_code=503, detail="User service is unavailable.")
