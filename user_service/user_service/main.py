from fastapi import FastAPI, Depends, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .dependencies import get_mock_supabase_client, get_supabase_cleint
from .mock_user import MockSupabaseClient
from .producer import get_kafka_producer
from .models import User, UserInfo, UserListResponse, UserMessage
from .settings import settings
from .notify_logic import notify_user_profile, notify_user_actions
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
    title='ONLINE SHOPPING MALL _ User Service',
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

@app.post("/user/signup", response_model=User)
async def register_user(
            payload: UserInfo,
            producer: AIOKafkaProducer = Depends(get_kafka_producer),
            client: MockSupabaseClient = Depends(get_client)
            ):
    user_data = {"username": payload.username, "email": payload.email, "password": payload.password}

    for existing_user in client.users:
        if existing_user["email"] == payload.email:
            raise HTTPException(status_code=400, detail="EMAIL_ALREADY_IN_USE")
    
    response = client.auth.sign_up(user_data)
    registered_user= response.get('user')
    generated_apikey= response.get('api_key')
    logging.info(f'GENERATED_API_KEY:{generated_apikey}')
    
    user_event_payload= User(
        username= payload.username,
        email= payload.email,
        password= payload.password,
        api_key= generated_apikey,
        action = 'Signup'
    )
    # USER_SIGNUP_NOTIFICATION
    await notify_user_actions(user_event_payload, producer)

    logging.info(f'REGISTERED_USER:{registered_user}')
    
    return registered_user

@app.post("/user/login")
async def login(
                payload: UserInfo,
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                client: MockSupabaseClient = Depends(get_client)):
    
    response = client.auth.login(payload)
    user_data = response.get("user")
    generated_apikey = user_data.api_key
    logging.info(f'GENERATED_API_KEY:{generated_apikey}')

    message_payload = User(
        username=payload.username,
        email=payload.email, 
        password=payload.password,
        api_key=generated_apikey,
        action="Login"
        )

    await notify_user_actions(message_payload, producer)

    return user_data


@app.get("/user/profile")
async def get_user_profile(
        api_key: str = Header(..., alias="apikey"),  # Match the alias to Kong "apikey"
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        client: MockSupabaseClient =Depends(get_client)
        ):
    
    response = client.auth.user_profile(api_key)
    if response.get("status") == "failed":
        return {"error": response["error"], "status": "failed"}
    
    user = response.get("user")
    if not user:
        return {"error": "User profile not found", "status": "failed"}

    user_message = UserMessage(action="get_user_profile", user=user)
    await notify_user_profile(user_message, producer)
    
    return response

@app.get("/user/profile/{user_id}")
async def get_user_profile(
            user_id: int,
            client: MockSupabaseClient = Depends(get_client)
            ):
    user = client.auth.get_user_by_id(user_id)  # Implement this in your MockSupabaseClient
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


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


