from fastapi import HTTPException
from .models import User, LoginInfo
from .database import supabase
from .models import MockTable
import logging, secrets, json, uuid

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

        logging.info(f"Attempting login with email: {email} and password: {password}")

        response = supabase.from_('mockuser').select('*').eq('email', payload.email).execute()
        # Convert to string
        response_str = response.json()
        # Convert string to dictionary
        response_dict= json.loads(response_str)

        for my_user in response_dict.get('data', []):
            if my_user["email"] == email and my_user["password"] == password:
                self.users.append(my_user)
                return my_user
        return {"CREDENTIALS_MISMATCHED"}

    def user_profile(self, payload_apikey):
            response= supabase.table('mockuser').select('*').eq('api_key', payload_apikey).execute()
            user_data= response.data
            return user_data 

    def get_users_list(self):
            response= supabase.table('mockuser').select('*').execute()
            users_list= response.data
            return users_list 
