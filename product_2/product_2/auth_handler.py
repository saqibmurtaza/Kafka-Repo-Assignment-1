from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from .settings import settings
from .validation_logic import validate_api_key
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import logging, jwt

class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request:Request, call_next):
        
        # Extract it from Headers
        apikey= request.headers.get('apikey')
        token= request.headers.get('token')

        logging.info(f"TOKEN*****{token}")

        try:
            # Decode Token, it verifies the login details
            decoded_token= jwt.decode(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
            email_in_token= decoded_token.get('email')
            logging.info(f"EMAIL IN TOKEN : {email_in_token}")
            """
            Extract user_profile from user_service with email extracted
            from Token - it checks that user is registered or not.
            only Registered user get token at the time of login
            """
            user_profile= validate_api_key(apikey, token)

            """
            1: Now check the email extracted from userprofile match with 
            email extracted from token
            2: Store the user's info in the request_context--This allows to 
            avoid making repeated API calls or database queries for user data, 
            as the information is already available in the request context.
            Request_Context, typically refers to data that is available 
            throughout the handling of a single HTTP request
            """
            if user_profile: # This checks if get_user_profile is truthy (i.e., not empty or None)
                for my_user in user_profile:
                    if my_user['email'] == email_in_token:
                        # store user_data in request_context
                        request.state.email= email_in_token
                        request.state.apikey= apikey
                        request.state.token= token
                        request.state.role= my_user.get('role', 'my_user')
                        break
                else:
                    raise HTTPException(status_code=403, detail="EMAIL_MISMATCHED")

            # Call the next route handler
            response = await call_next(request)
            return response
        
        except jwt.exceptions.DecodeError as e:
            logging.error(f"JWT Decode Error: {str(e)}")
            raise HTTPException(status_code=400, detail="INVALID_TOKEN_FORMAT_OR_NOT_FOUND_IN_REQUEST")
