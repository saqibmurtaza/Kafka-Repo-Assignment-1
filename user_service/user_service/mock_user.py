from .models import User, LoginInfo
import logging, secrets

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

def generate_api_key():
    return secrets.token_hex(16)  # Generates a 32-character hex string

class MockSupabaseClient():
    def __init__(self):
        self.users= [] # list of dicts/objects will save in it
        self.auth= MockSupabaseAuth(self.users)
   
    def table(self, name: str):
        if name == 'mock_user':
            return MockTable(self.users)
        raise ValueError(f"NO_MOCK_TABLE_FOR_NAME {name}")

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


    def login(self, payload: LoginInfo):
        email = payload.email
        password = payload.password

        for my_user in self.users:
            if my_user["email"] == email and my_user["password"] == password:
            # Extract Data from self.users
                user_data= {
                    "user": User(
                            email=my_user["email"],
                            password=my_user["password"],
                            api_key=my_user['api_key']
                                )
                }
                return user_data
        return {"error": "CREDENTIALS_MISMATCHED", "status": "FAILED"}

    def user_profile(self, api_key: str):
        # Find user by API key
        for user in self.users:
            if user.get("api_key") == api_key:
                return {"user": User(**user), "status": "success"}
        return {"error": "User Profile not found", "status": "failed"}


class MockTable:
    def __init__(self, data):
        self._data = data  # Use a private variable to hold the data <---
        self.filtered_data = data  # Initialize filtered data to be the same as input data

    @property
    def data(self):
        return self.filtered_data

    def select(self, *args, **kwargs):
        # Mimic select functionality, for simplicity 
        # assume it returns the filtered data
        return self


    def eq(self, column_name, value):
        # Filter data based on column and value, 
        # assuming data is a list of dictionaries
        self.filtered_data = [item for item in self._data if item.get(column_name) == value]
        return self

    def execute(self):
        # Mimic the behavior of an execute method in the supabase client
        return self
