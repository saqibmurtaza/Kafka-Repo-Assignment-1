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

            # Validate API key and user profile
            user_profile = validate_api_key(apikey, token)
            email_in_profile = None 

            if isinstance(user_profile, dict): 
                if "email" in user_profile: 
                    email_in_profile = user_profile.get("email") 
                
                elif "user" in user_profile and isinstance(user_profile["user"], list): 
                    for user in user_profile["user"]: 
                        if user.get("email") == email_in_token: 
                            email_in_profile = user.get("email") 
                            break 
            if email_in_profile == email_in_token: 
                request.state.email = email_in_token 
                request.state.role = role

                restricted_routes = {
                    "/product": {
                        "POST": "admin",  # Only admins can create a product
                        "GET": "user",    # Users can view the catalogue
                        },
                    "/product/{id}": {
                        "PUT": "admin",   # Only admins can update a catalogue item
                        "GET": "user",    # Users can track a specific catalogue item
                        "DELETE": "admin" # Only admins can delete a catalogue item
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
                logging.info(f"REQUIRED ROLE: {required_role}")

                if role == "admin" or (required_role and role == required_role):  # <---- Added condition to allow admins to bypass role check
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
