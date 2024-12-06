# from fastapi import Request, HTTPException
# from starlette.middleware.base import BaseHTTPMiddleware
# from ..settings import settings
# from ..validation_logic import validate_api_key
# import logging, jwt

# class AuthMiddleware(BaseHTTPMiddleware):

#     async def dispatch(self, request:Request, call_next):
        
#         # Extract it from Headers
#         apikey= request.headers.get('apikey')
#         token= request.headers.get('token')

#         if not token:
#             raise HTTPException(status_code=403, detail="Token missing in request headers")

#         # Decode Token, it verifies the login details
#         decoded_token= jwt.decode(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
#         email_in_token= decoded_token.get('email')

#         """
#         Extract user_profile from user_service with email extracted
#         from Token - it checks that user is registered or not.
#         only Registered user get token at the time of login
#         """
#         user_profile= validate_api_key(apikey, token)

#         """
#         1: Now check the email extracted from userprofile match with 
#         email extracted from token
#         2: Store the user's info in the request_context--This allows to 
#         avoid making repeated API calls or database queries for user data, 
#         as the information is already available in the request_context.
#         Request_Context, typically refers to data that is available 
#         throughout the handling of a single HTTP request
#         """
#         if user_profile: # This checks if get_user_profile is truthy (i.e., not empty or None)
#             for my_user in user_profile:
                
#                 if my_user['email'] == email_in_token:
#                 # store user_data in request_context
#                     request.state.email= email_in_token
#                     request.state.apikey= apikey
#                     request.state.token= token
#                     request.state.role= my_user.get('role', 'my_user')
#                     break
#             else:
#                 raise HTTPException(status_code=403, detail="Invalid API Key or email mismatch")

#         # Call the next route handler
#         response = await call_next(request)
#         return response

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from .settings import settings
from .validation_logic import validate_api_key
import logging, jwt, re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        apikey = request.headers.get("apikey")
        token = request.headers.get("token")

        try:
            # Decode JWT Token
            decoded_token = jwt.decode(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
            email_in_token = decoded_token.get("email")
            role = decoded_token.get("role")
            logging.info(f"EXTRACTED_ROLE_FROM_TOKEN: {role}")

            # Validate API key and user profile
            user_profile = validate_api_key(apikey, token)
            email_in_profile = None 

            if isinstance(user_profile, dict): 
                if "email" in user_profile: 
                    email_in_profile = user_profile.get("email")
                    logging.info(f"EXTRACTED_EMAIL_FROM_PROFILE: {email_in_profile}") 
                
                elif "user" in user_profile and isinstance(user_profile["user"], list): 
                    for user in user_profile["user"]: 
                        if user.get("email") == email_in_token: 
                            email_in_profile = user.get("email")
                            role_in_profile = user.get("role")
                            logging.info(f"EXTRACTED_ROLE_FROM_PROFILE: {role_in_profile}")
                            break

            if email_in_profile == email_in_token: 
                request.state.email = email_in_token 
                request.state.role = role
                request.state.apikey = apikey

                restricted_routes = {
                    "/inventory": {
                        "POST": "admin",  # Only admins can create inventory
                        "GET": "user",    # Users can view stock
                        },
                    "/inventory/{id}": {
                        "PUT": "admin",   # Only admins can update a stock item
                        "GET": "user",    # Users can track a specific stock item
                        "DELETE": "admin" # Only admins can delete a stock item
                        },
                    }

                # Function to match path with parameters
                def match_path(path, routes):
                    for route in routes:
                        pattern = re.sub(r'{[^/]+}', '[^/]+', route)
                        if re.fullmatch(pattern, path):
                            return routes[route]
                    return None

                # Debugging logs
                logging.info(f"Request Path: {request.url.path}")
                logging.info(f"Request Method: {request.method}")

                matched_route = match_path(request.url.path, restricted_routes)
                required_role = matched_route.get(request.method) if matched_route else None
                logging.info(f"MENTIONED_ROLE_ALLOW_TO_ACCESS: {required_role}")

                if role == "admin" or (required_role and role == required_role):  # Added condition to allow admins to bypass role check
                # if role_in_profile == "admin" or (required_role and role_in_profile == required_role):  # Added condition to allow admins to bypass role check
                    response = await call_next(request)
                    return response
                else:
                    logging.warning(
                        f"ACCESS_DENIED: {request.url.path} requires {required_role} role. User role: {role}, Email: {email_in_token}"
                    )
                    raise HTTPException(status_code=403, detail=f"ACCESS_DENIED: {required_role} role required")

            else:
                logging.warning(f"EMAIL_MISMATCHED: {email_in_token} does not match user profile email {user_profile.get('email')}")
                raise HTTPException(status_code=403, detail="EMAIL_MISMATCHED")

        except HTTPException as e:
            logging.error(f"HTTPException raised: {e.detail}")
            return Response(content=e.detail, status_code=e.status_code)
