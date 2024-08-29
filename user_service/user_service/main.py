from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional, Union, Dict
from .dependencies import get_mock_supabase_client, get_supabase_cleint
from .mock_supabase import MockSupabaseClient
from .producer import get_kafka_producer
from .models import User, UserRegistration,UserListResponse, LoginRequest, UserMessage, Token, ActionEnum
from .settings import settings
from .notify_logic import notify_user_profile, notify_user_registration, send_token
from aiokafka import AIOKafkaProducer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info(f"""
    !**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!
    WELCOME TO ONLINE SHOPPING MALL!
    Explore a wide variety of products tailored to your needs.
    Enjoy seamless shopping with secure payments and fast delivery.
    Don't miss out on our exclusive offers and discounts!
    Happy shopping!
    !**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!
    """)
    yield
    logging.info(f"THANK YOU FOR VISITING OUR ONLINE SHOPPING MALL. WE HOPE TO SEE YOU AGAIN SOON!")

app = FastAPI(
    lifespan=lifespan,
    title='ShopSphere _ User Service',
    servers=[
        {
            "url": "http://localhost:8009",
            "description": "Server: Uvicorn, port: 8009"
        }
    ]
)

def get_client():
    if settings.MOCK_SUPABASE:
        return get_mock_supabase_client()
    else:
        return get_supabase_cleint()

@app.get("/")
def read_root():
    return {"message": "User_Service"}

@app.post("/user/action")
async def send_manual_request(
    payload_action: ActionEnum,
    producer: AIOKafkaProducer = Depends(get_kafka_producer)
    ):
    await producer.send(settings.TOPIC_USER_EVENTS, payload_action.value.encode('utf-8'))

    return {"message": "Action received", "action": payload_action.value}

@app.post("/user/signup", response_model=User)
async def register_user(
        payload: UserRegistration,
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        client: MockSupabaseClient = Depends(get_client)
        ):
    user_data = {"username": payload.username, "email": payload.email, "password": payload.password}
    if payload.action != "Signup":
        raise HTTPException(status_code=400, detail="Invalid action. Action must be 'Signup'.")

    for existing_user in client.users:
        if existing_user["email"] == payload.email:
            raise HTTPException(status_code=400, detail="EMAIL_ALREADY_IN_USE")
    
    response = client.auth.sign_up(user_data)
    registered_user= response['user']

    user_event_payload= UserRegistration(
        username= payload.username,
        email= payload.email,
        password= payload.password,
        action= payload.action
    )
    # USER_SIGNUP_NOTIFICATION
    await notify_user_registration(user_event_payload, producer)
   
    return registered_user

@app.post("/user/login")
async def login(
                payload: LoginRequest,
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                client: MockSupabaseClient = Depends(get_client)):
    response = client.auth.login(payload)

    if payload.action != "Login":
        raise HTTPException(status_code=400, detail="Invalid action. Action must be 'Signup'.")

    if "error" in response:
        raise HTTPException(status_code=500, detail=response)
    
    user = response["user"]
    token = response["token"].access_token

    # Create Token and LoginRequest instances
    token_payload = Token(
        access_token=token
        )
    message_payload = LoginRequest(
        username=payload.username,
        email=payload.email, 
        password=payload.password,
        action=payload.action
        )

    await send_token(token_payload, message_payload, producer)
    
    return {"user": user,  "token": token_payload}

@app.get("/user/profile")
async def get_user_profile(
        token: str = Query(..., alias="token"),
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        client: MockSupabaseClient = Depends(get_client)):
    
    response = client.auth.user_profile(token)
    if response.get("status") == "failed":
        return {"error": response["error"], "status": "failed"}
        
    user = response["user"]
    if not user:
        return {"error": "User profile not found", "status": "failed"}

    user_message = UserMessage(action="get_user_profile", user=user)
    await notify_user_profile(user_message, producer)
    
    return response

@app.get("/user", response_model=list[UserListResponse])
def get_users_list(client: MockSupabaseClient = Depends(get_client)):
    users_list = client.users
    filtered_users = [{"username": user["username"], "email": user["email"]} for user in users_list]

    logging.info(f'List of Registered Users : {filtered_users}')
    return filtered_users

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://localhost:8000",
    "https://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://localhost:8001",
    "https://localhost:8001",
    "https://127.0.0.1:8001",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://localhost:8080",
    "https://127.0.0.1:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


