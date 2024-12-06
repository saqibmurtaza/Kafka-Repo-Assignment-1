from fastapi import HTTPException
from .models import User, LoginInfo
from .database import supabase
from .models import MockTable
from .settings import settings
from datetime import datetime, timedelta, timezone
import logging, secrets, json, uuid, jwt

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

def generate_api_key():
    return secrets.token_hex(16)

def generate_unique_id():
    return str(uuid.uuid4())

class MockSupabaseClient():
    def __init__(self):
        self.users = []
        self.auth= MockSupabaseAuth(self.users)

    def table(self, name: str):
        if name == 'mockuser':
            return MockTable(self.users)
        raise ValueError(f"NO_MOCK_TABLE_FOR_NAME {name}")
 
class MockSupabaseAuth():
    def __init__(self, user):
        self.users= user

    def sign_up(self, user_data):
        # Generate a unique id first
        user_data["id"] = generate_unique_id()
        user_data["api_key"] = generate_api_key()
        
        response = supabase.from_('mockuser').select('*').eq('email', user_data['email']).execute()

        # Convert to string
        response_str = response.json()
        # Convert string to dictionary
        existing_user_dict= json.loads(response_str) 

        for my_user in existing_user_dict.get('data', []):
            if my_user["email"] == user_data["email"]:
                return {"user":"USER_ALREADY_EXIST"}
            self.users.append(user_data)
            logging.info(f'`ID: {user_data['id']}')
        return {
            "user": User(**user_data)
            }

    def login(self, payload: LoginInfo):
        email = payload.email
        password = payload.password

        response = supabase.from_('mockuser').select('*').eq('email', payload.email).execute()
        # Convert to string
        response_str = response.json()
        # Convert string to dictionary
        response_dict= json.loads(response_str)

        for my_user in response_dict.get('data', []):
            if my_user["email"] == email and my_user["password"] == password and my_user["role"]:
                
                email= my_user.get('email')
                password= my_user.get('password')
                role= my_user.get('role')
                
                token= generate_token(email, password, role, expires_in_hours=15) 
                return {
                    "token" : token,
                    "user": my_user,
                    "role": role
                }
        return {"CREDENTIALS_MISMATCHED"}

    def user_profile(self, payload_apikey):
            response= supabase.table('mockuser').select('*').execute()
            user_data= response.data # you get the list of dicts stored in key 'data'
            logging.info(f"EXTRACTED_DB-DATA:{user_data}")
            return user_data 

def generate_token(email, password, role, expires_in_hours):
    payload= {
        "email": email,
        "password": password,
        "role": role,
        "exp": datetime.now(timezone.utc)+timedelta(hours=expires_in_hours)
    }
    token= jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    return token

def get_user_role_by_email(email: str):
    response= supabase.from_('mockuser').select('*').eq('email', email ).execute()
    response_str= response.json() # convert it to json-string
    response_dict= json.loads(response_str)  # Convert string to dictionary
    
    logging.info(f"DATA_FROM_DB : {response_dict}")

    for my_user in response_dict.get('data', []):
        if my_user['email'] == email:
            role= my_user['role']
            return role
        logging.info(f"USER_DATA_NOT_FOUND")
    None


    

