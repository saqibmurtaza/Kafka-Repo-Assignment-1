from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .dependencies import get_mock_supabase_client, get_supabase_cleint
from .consumer import start_consumer
from .mock_supabase import MockSupabaseClient
from .producer import get_kafka_producer
from .models import User, UserListResponse
from .settings import settings
from .notifications_logic import send_notification, NotificationPayload, notify_order_status
from aiokafka import AIOKafkaProducer
from pydantic import BaseModel
import logging, asyncio, json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app=FastAPI):
    logging.info('Consumer Task processing...')
    topics= [settings.TOPIC_USER_EVENTS]
    consumer_task = asyncio.create_task(
        start_consumer(
            topics,
            bootstrap_server='broker:9092',
            consumer_group_id=settings.CONSUMER_GROUP_NOTIFYME_MANAGER
        )
    )
    try:
        yield
    finally:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            print("Consumer Task cancelled")

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
        return get_supabase_cleint

class UserMessage(BaseModel):
    action: str
    user: User

@app.get("/")
def read_root():
    return {"message": "User_Service"}

@app.post("/user/registration", response_model=User)
async def register_user(
        user: User,
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        client: MockSupabaseClient = Depends(get_client)):
    user_data = {"username": user.username, "email": user.email, "password": user.password}
    for existing_user in client.users:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already in use")
    response = client.auth.sign_up(user_data)
    client.auth.print_users()
    #update id in user from response from auth.signup
    user.id = response['user'].id
    user_message = UserMessage(action="register", user=user)
    await send_notification(producer, 
                            settings.TOPIC_USER_EVENTS, 
                            user_message)
    
    # Send notification
    notification_payload = NotificationPayload(
        user_email=user.email,
        status="registered",
        order_id=user.id
    )
    await notify_order_status(notification_payload)
    
    return user
@app.post("/user/login")
async def login(email: str, password: str,
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                client: MockSupabaseClient = Depends(get_client)):
    response = client.auth.login(email, password)
    if isinstance(response, dict) and "error" in response:
        raise HTTPException(status_code=500, detail=response)
    
    user = response["user"]  # Get the user object directly
    
    user_message = UserMessage(action="login", user=user)
    await send_notification(producer, settings.TOPIC_USER_EVENTS, user_message)
    
    # Send notification
    notification_payload = NotificationPayload(
        user_email=user.email,
        status="logged_in",
        order_id=user.id
    )
    await notify_order_status(notification_payload)
    
    return {"user": user, "token": response["token"]}

@app.get("/user/profile")
async def get_user_profile(token: str, 
                           producer: AIOKafkaProducer = Depends(get_kafka_producer),
                           client: MockSupabaseClient = Depends(get_client)):
    response = client.auth.user_profile(token)
    if response.get("status") == "failed":
        return {"error": response["error"], "status": "failed"}
        
    user = response["user"]
    if not user:
        return {"error": "User profile not found", "status": "failed"}

    user_message = UserMessage(action="get_user_profile", user=user)
    await send_notification(producer, 
                            settings.TOPIC_USER_EVENTS, 
                            user_message)
    
    # Send notification
    notification_payload = NotificationPayload(
        user_email=user.email,
        status="profile_viewed",
        order_id=user.id
    )
    await notify_order_status(notification_payload)
    
    return response

@app.get("/user/list", response_model=list[UserListResponse])
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
