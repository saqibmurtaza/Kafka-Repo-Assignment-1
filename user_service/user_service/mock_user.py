from .models import LoginRequest
from .models import User
import logging, secrets

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

def generate_api_key():
    return secrets.token_hex(16)  # Generates a 32-character hex string

class MockSupabaseClient():
    def __init__(self):
        self.users= [] # list of dicts/objects will save in it
        self.auth= MockSupabaseAuth(self.users)

class MockSupabaseAuth():
    def __init__(self, user):
        self.users= user

    def sign_up(self, user_data):
        for my_user in self.users:
            if my_user["email"] == user_data["email"]:
                return {"error": "User already exists"}
        user_data["id"] = len(self.users) + 1
        user_data["api_key"] = generate_api_key()  # Generate API key for the user
        self.users.append(user_data)
        logging.info(f'SELF.USER:{self.users}')
        return {
            "user": User(**user_data),
            "api_key": user_data["api_key"]
            }

    def login(self, login_request: LoginRequest):
        email = login_request.email
        password = login_request.password

        for my_user in self.users:
            if my_user["email"] == email and my_user["password"] == password:
            # Extract Data from self.users
                user_data= {
                    "user": User(id=my_user["id"], 
                                username=my_user["username"], 
                                email=my_user["email"], 
                                password=my_user["password"],
                                api_key=my_user['api_key']
                                )
                }
                
                return user_data
        return {"error": "Credentials Mismatched", "status": "failed"}

    def user_profile(self, api_key: str):
        # Find user by API key
        for user in self.users:
            if user.get("api_key") == api_key:
                return {"user": User(**user), "status": "success"}
        return {"error": "User Profile not found", "status": "failed"}
