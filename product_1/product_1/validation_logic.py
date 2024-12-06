from fastapi import HTTPException
from starlette.responses import Response
import requests
import logging, json

def validate_api_key(apikey: str, token: str):
    try:
        response = requests.get(
            "http://user_service:8009/user/profile",
            headers={"apikey": apikey, "token": token},
            timeout=10
        )
        
        response.raise_for_status()
        response_json = response.json()
        
        return response_json
    
    except requests.ConnectionError:
        logging.error('CONNECTION_REFUSED_TO_USER_SERVICE')
        raise HTTPException(status_code=503, detail="User service is unavailable.")
    
    except requests.HTTPError as http_err:
        logging.error(f"HTTP_ERROR: {http_err}")
        raise HTTPException(status_code=http_err.response.status_code, detail="User service returned an error")
    
    except Exception as err:
        logging.error(f"UNEXPECTED_ERROR: {err}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    except HTTPException as e:
            logging.error(f"HTTPException raised: {e.detail}")
            return Response(content=e.detail, status_code=e.status_code)
