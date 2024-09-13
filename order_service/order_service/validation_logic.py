from fastapi import Header, HTTPException
import httpx, requests
import logging

def validate_api_key(apikey:str):
    try:
        response = requests.get(
            "http://user_service:8009/user/profile", 
            headers={"apikey": apikey},
            timeout=10
        )

        if response.raise_for_status:
            response_json = response.json()
    
            if isinstance(response_json, dict) and 'user' in response_json:
                return response_json.get("user")  # Return user data if present

        # Handle invalid API key
        raise HTTPException(status_code=403, detail="INVALID_API_KEY")

    except httpx.ConnectError:
        logging.error('CONNECTION_REFUSED_TO_USER_SERVICE')
        raise HTTPException(status_code=503, detail="User service is unavailable.")
