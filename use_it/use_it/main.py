from fastapi import FastAPI, Depends, HTTPException, Body
from .dependencies import get_mock_supabase_client, get_supabase_client
from .mock_supabase import MockSupabaseClient
from models import User
from use_it import settings
from aiokafka import AIOKafkaProducer
from .producer import get_kafka_producer
from pydantic import BaseModel
import os, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
mock_supabase = os.getenv('MOCK_SUPABASE', 'true').lower() == 'true'

app = FastAPI()

def get_client():
    if mock_supabase:
        return get_mock_supabase_client()
    else:
        return get_supabase_client()

class UserMessage(BaseModel):
    action: str
    user: User

@app.get("/")
def read_root():
    return {"message": "User_Profile_Practice_Code"}

@app.post("/register_user", response_model=User)
async def register_user(user: User, 
                        producer: AIOKafkaProducer = Depends(get_kafka_producer), 
                        client: MockSupabaseClient = Depends(get_client),
                        topic:str=settings.TOPIC_USER_EVENTS):
    user_data = {"username": user.username, "email": user.email, "password": user.password}
    for existing_user in client.users:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already in use")
    response = client.auth.sign_up(user_data)
    client.auth.print_users()
    user_message = UserMessage(action="register", user=user)
    await producer.send_and_wait(topic, user_message.json().encode('utf-8'))
    return response

@app.post("/login")
async def login(email: str, password: str, 
                producer: AIOKafkaProducer = Depends(get_kafka_producer), 
                client: MockSupabaseClient = Depends(get_client),
                topic:str=settings.TOPIC_USER_EVENTS):
    response = client.auth.login(email, password)
    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=500, detail=response)
    user_message = UserMessage(action="login", user=response["user"])
    await producer.send_and_wait(topic, user_message.json().encode('utf-8'))
    return {"user": response["user"], "token": response["token"]}

@app.get("/user_profile")
async def get_user_profile(token: str, client: MockSupabaseClient = Depends(get_client)):
    response = client.auth.user_profile(token)
    if response.get("status") == "failed":
        return {"error": response["error"], "status": "failed"}
    return response

@app.get("/users_list", response_model=list[User])
def get_users_list(client: MockSupabaseClient = Depends(get_client)):
    users_list = client.users
    logging.info(f'List of Registered Users : {users_list}')
    return users_list
