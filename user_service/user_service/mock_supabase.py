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
            self.parent.users.append(user_data)  # Adding user data to the parent list
            print(f"User registered: {user_data}")  # Debug print
            return {"error": None, "data": {"user": {"id": "user_id", "email": user_data["email"]}}}

        def sign_in(self, email, password):
            for user in self.parent.users:
                if user["email"] == email and user["password"] == password:
                    self.access_token = "fake_token"  # Mock access token
                    return {"error": None, "data": {"access_token": self.access_token}}
            return {"error": {"message": "Invalid credentials"}}

        def set_access_token(self, access_token):
            self.access_token = access_token

        def user(self):
            if self.access_token:
                # Find user based on access token or return a default user
                for user in self.parent.users:
                    if user["email"] == "test@example.com":
                        return user
                return {"username": "testuser", "email": "test@example.com", "password": "password"}
            else:
                return {"message": "No access token set"}

def get_mock_supabase_client():
    return MockSupabaseClient()
