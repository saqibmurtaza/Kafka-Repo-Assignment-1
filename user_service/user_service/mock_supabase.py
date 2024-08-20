from datetime import datetime, timedelta, timezone
from .models import LoginRequest
from .models import User, Token
import logging, sys, os, jwt

# PACKAGE_ROOT = os.path.dirname(os.path.realpath(__file__))
# sys.path.insert(0, PACKAGE_ROOT)



logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

class MockSupabaseClient():
    def __init__(self):
        self.users= [] # list of dicts will save in it
        self.auth= MockSupabaseAuth(self.users)

class MockSupabaseAuth():
    def __init__(self, user):
        self.users= user
        self.access_token= None

    def sign_up(self, user_data):
        for my_user in self.users:
            if my_user["email"] == user_data["email"]:
                return {"error": "User already exists"}
        user_data["id"] = len(self.users) + 1
        self.users.append(user_data)
        return {"user": User(**user_data)}
    
    def login(self, login_request: LoginRequest):
        email = login_request.email
        password = login_request.password
        
        for my_user in self.users:
            if my_user["email"] == email and my_user["password"] == password:
                access_token = generate_fake_token(my_user["id"], my_user["email"], expires_in_hours=1)
                logging.info(f'Generated_Token : {access_token}')
                decoded = jwt.decode(access_token, "My_Secret_Key", algorithms=["HS256"])
                logging.info(f'TOKEN-DECODED : {decoded}')
                
                return {"user": User(id=my_user["id"], username=my_user["username"], email=my_user["email"], password=my_user["password"]), 
                        "token": Token(access_token=access_token),
                        "status": "success"}
        
        return {"error": "Credentials Mismatched", "status": "failed"}

    def user_profile(self, access_token: str):
        try:
            payload = jwt.decode(access_token, JWT_SECRET, 
                                 algorithms=["HS256"])
            user_id = payload["user_id"]
            for user in self.users:
                if user["id"] == user_id:
                    # return {"data": user, "status": "success"}
                    return {"user": User(**user), "status": "success"}
            return {"error": "User Profile not found", "status": "failed"}
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired", "status": "failed"}
        except jwt.DecodeError:
            return {"error": "Invalid token", "status": "failed"}



JWT_SECRET = "My_Secret_Key"  
def generate_fake_token(user_id, email, expires_in_hours):  
    payload = {  
        "user_id": user_id,  
        "email": email,  
        "exp": datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),  
        "iss": "My_Secret_Key"  

    }  
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")  
    return token  


