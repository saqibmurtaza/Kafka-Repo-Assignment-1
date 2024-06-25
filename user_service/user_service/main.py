import os
import logging
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from .dependencies import get_supabase_client, get_mock_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

USE_MOCK_SUPABASE = os.getenv("USE_MOCK_SUPABASE", "true").lower() == "true"

def get_client():
    if USE_MOCK_SUPABASE:
        return get_mock_supabase_client()
    else:
        return get_supabase_client()

class User(BaseModel):
    username: str
    email: str
    password: str

@app.post("/register", response_model=User)
async def register_user(user: User, supabase_client=Depends(get_client)):
    user_data = {"username": user.username, "email": user.email, "password": user.password}
    response = supabase_client.auth.sign_up(user_data)
    if response["error"]:
        raise HTTPException(status_code=400, detail=f"Error signing up: {response['error']['message']}")
    return user

@app.post("/login")
async def login_user(email: str, password: str, supabase_client=Depends(get_client)):
    response = supabase_client.auth.sign_in(email=email, password=password)
    if response["error"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = response["data"]["access_token"]
    logging.info(f'Access_token={access_token}')
    return {"access_token": access_token}

@app.get("/profile", response_model=User)
async def get_user_profile(authorization: str = Header(...), supabase_client=Depends(get_client)):
    logging.info(f'Authorization header received: {authorization}')
    try:
        token = authorization.split("Bearer ")[1]
        logging.info(f'Extracted token: {token}')
    except IndexError:
        logging.error("Invalid authorization header format")
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    try:
        supabase_client.auth.set_access_token(token)
        user_profile = supabase_client.auth.user()
        logging.info(f'User profile retrieved: {user_profile}')
        
        supabase_client.auth.set_access_token(token)
        user_profile = supabase_client.auth.user()
        if "error" in user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        return user_profile
    except Exception as e:
        logging.exception("Error retrieving user profile")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/mock-users", response_model=list[User])
async def get_mock_users(supabase_client=Depends(get_client)):
    return supabase_client.users  # Return the list of mock users stored in MockSupabaseClient
