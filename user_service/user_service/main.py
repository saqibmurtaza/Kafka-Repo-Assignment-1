import os, supabase, logging
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from .mock_supabase import get_mock_supabase_client, MockSupabaseClient

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

app = FastAPI()

USE_MOCK_SUPABASE = os.getenv("USE_MOCK_SUPABASE", "true").lower() == "true"

if USE_MOCK_SUPABASE:
    supabase_client = get_mock_supabase_client()
else:
    # Initialize the real Supabase client
    supabase_url = "https://nueavvbhalbwtwtgpejb.supabase.co"
    supabase_key = "your-supabase-key"
    supabase_client = supabase.create_client(supabase_url, supabase_key)

class User(BaseModel):
    username: str
    email: str
    password: str

@app.post("/register", response_model=User)
async def register_user(user: User):
    user_data = {"username": user.username, "email": user.email, "password": user.password}
    response = supabase_client.auth.sign_up(user_data)
    if response["error"]:
        raise HTTPException(status_code=400, detail=f"Error signing up: {response['error']['message']}")
    return user

@app.post("/login")
async def login_user(email: str, password: str):
    response = supabase_client.auth.sign_in(email=email, password=password)
    if response["error"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token= response["data"]["access_token"]
    logging.info(f'Access_token={access_token}')
    return access_token

@app.get("/profile", response_model=User)
async def get_user_profile(authorization: str = Header(...)):
    access_token = authorization.split("Bearer ")[1]
    supabase_client.auth.set_access_token(access_token)
    user_profile = supabase_client.auth.user()
    return user_profile

@app.get("/mock-users", response_model=list[User])
async def get_mock_users():
    return supabase_client.users  # Return the list of mock users stored in MockSupabaseClient
