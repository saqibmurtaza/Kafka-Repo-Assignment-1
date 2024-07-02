import logging, jwt
from datetime import datetime, timedelta, timezone
import sys, os

PACKAGE_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, PACKAGE_ROOT)

from models import User, Token

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

class MockSupabaseClient():
    def __init__(self):
        self.users= []
        self.auth= MockSupabaseAuth(self.users)

class MockSupabaseAuth():
    def __init__(self, user):
        self.users= user
        self.access_token= None

    def sign_up(self, user_data):
        for my_user in self.users:
            if my_user["email"] == user_data["email"]:
                return user_data

        user_data["id"] = len(self.users) + 1
        self.users.append(user_data)
        return user_data
    
    def print_users(self):
        print("Current Users:")
        for user in self.users:
            print(user)

    def login(self, email, password):
        for user in self.users:
            if user["email"] == email and user["password"] == password:
                access_token = generate_fake_token(user["id"], user["email"])
                logging.info(f'Access_token : {access_token}')
                return {"user": User(id=user["id"], username=user["username"], email=user["email"], password=user["password"]), "token": Token(access_token=access_token)}
        return {"error": "Credentials Mismatched", "status": "failed"}

    def user_profile(self, access_token: str):
        try:
            payload = jwt.decode(access_token, JWT_SECRET, 
                                 algorithms=["HS256"])
            user_id = payload["user_id"]
            for user in self.users:
                if user["id"] == user_id:
                    return {"data": user, "status": "success"}
            return {"error": "User not found", "status": "failed"}
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired", "status": "failed"}
        except jwt.DecodeError:
            return {"error": "Invalid token", "status": "failed"}


JWT_SECRET= "My_Secret_Key"
def generate_fake_token(user_id, email):
    payload= {
        "user_id" : user_id,
        "email" : email,
        "exp" : datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token= jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token
