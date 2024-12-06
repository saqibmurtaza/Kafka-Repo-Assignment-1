from fastapi import HTTPException
import requests
import logging

def validate_api_key(apikey:str, token:str):
    try:
        response = requests.get(
            "http://user_service:8009/user/profile", 
            headers={
                "apikey": apikey,
                "token" : token,
                },
            timeout=10
        )
        response.raise_for_status()
        response_json = response.json()
        
        if isinstance(response_json, dict) and 'user' in response_json:
            user= response_json.get("user")  # Return user data if present
            return user
        
        raise HTTPException(status_code=404, detail="USER_DATA_NOT_FOUND")

    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        raise HTTPException(status_code=403, detail="INVALID_API_KEY_TOKEN_OR_EMAIL")

    except requests.exceptions.ConnectionError:
        logging.error('CONNECTION_REFUSED_TO_USER_SERVICE')
        raise HTTPException(status_code=503, detail="User service is unavailable")