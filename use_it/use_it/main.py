import os, logging
from fastapi import FastAPI, Depends, HTTPException
from .dependencies import get_mock_supabase_client, get_supabase_cleint
from .mock_supabase import MockSupabaseClient
from models import User

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)
mock_supabase=os.getenv('MOCK_SUPABASE', 'true').lower() == 'true'

app= FastAPI()

def get_client():
    if mock_supabase:
        return get_mock_supabase_client()
    else:
        get_supabase_cleint()

@app.get("/")
def read_root():
    return {"message": "User_Profile_Practice_Code"}

@app.post("/register_user", response_model=User)
def register_user(user:User, client:MockSupabaseClient=Depends(get_client)):
    user_data= {"username":user.username, "email":user.email, "password":user.password}
    for existing_user in client.users:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already in use")
    response= client.auth.sign_up(user_data)
    client.auth.print_users()
    return response

@app.post("/login")
def login(email: str, password: str, client: MockSupabaseClient = Depends(get_client)):
    response = client.auth.login(email, password)
    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=500, detail=response)
    return {"user": response["user"], "token": response["token"]}

@app.get("/user_profile")
def get_user_profile(token: str, client: MockSupabaseClient = Depends(get_client)):
    response = client.auth.user_profile(token)
    if response.get("status") == "failed":
        return {"error": response["error"], "status": "failed"}
    return response

@app.get("/users_list", response_model=list[User])
def get_users_list(client:MockSupabaseClient=Depends(get_client)):
    users_list= client.users
    logging.info(f'List of Registered Users : {users_list}')
    return users_list

