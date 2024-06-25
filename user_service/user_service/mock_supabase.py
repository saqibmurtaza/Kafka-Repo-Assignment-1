import jwt
from datetime import datetime, timedelta

# Secret key for signing JWTs (you can generate a secure random key for production)
JWT_SECRET = "your_jwt_secret_key"

def generate_fake_token(user_id, email):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token  # Return the token directly as a string

class MockSupabaseClient:
    _instance = None  # Class variable to hold the singleton instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MockSupabaseClient, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'users'):
            self.users = []  # In-memory storage for user data
        self.auth = self.Auth(self)

    class Auth:
        def __init__(self, parent):
            self.parent = parent
            self.access_token = None

        def sign_up(self, user_data):
            if "test@example.com" in user_data["email"]:
                return {"error": {"message": "Email rate limit exceeded"}}
            # Generate a unique ID (replace with actual unique ID generation logic)
            user_data["id"] = len(self.parent.users) + 1  # Example: Use length of users list as ID
            self.parent.users.append(user_data)  # Adding user data to the parent list
            print(f"User registered: {user_data}")  # Debug print
            return {"error": None, "data": {"user": {"id": user_data["id"], "email": user_data["email"]}}}

        def sign_in(self, email, password):
            for user in self.parent.users:
                if user["email"] == email and user["password"] == password:
                    # Generate a fake token for the user
                    self.access_token = generate_fake_token(user["id"], user["email"])
                    return {"error": None, "data": {"access_token": self.access_token}}
            return {"error": {"message": "Invalid credentials"}}

        def set_access_token(self, access_token):
            self.access_token = access_token

        def user(self):
            if self.access_token:
                # Decode the token to retrieve user email or return default user
                try:
                    payload = jwt.decode(self.access_token, JWT_SECRET, algorithms=["HS256"])
                    user_id = payload.get("user_id")
                    user_email = payload.get("email", "default@example.com")
                    for user in self.parent.users:
                        if user["id"] == user_id:
                            return user
                    return {"username": "default_user", "email": user_email, "password": "default_password"}
                except jwt.ExpiredSignatureError:
                    return {"message": "Token has expired"}
                except jwt.InvalidTokenError:
                    return {"message": "Invalid token"}
            else:
                return {"message": "No access token set"}

def get_mock_supabase_client():
    return MockSupabaseClient()

def get_supabase_client():
    # In real implementation, this function would initialize and return the actual Supabase client
    # For mock purposes, we return the mock client
    return get_mock_supabase_client()
