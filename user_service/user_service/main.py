from fastapi import FastAPI, Depends, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from supabase import Client
from typing import Union
from contextlib import asynccontextmanager
from .dependencies import get_mock_supabase_client, get_supabase_cleint, create_consumer_and_key
from .database import create_db_tables, get_session
from .mock_user import MockSupabaseClient
from .producer import get_kafka_producer
from .models import User, MockUser, UserInfo, UserListResponse, UserMessage, NotifyUser, LoginInfo
from .settings import settings
from .notify_logic import notify_user_profile, notify_user_actions
from aiokafka import AIOKafkaProducer
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('CREATING_DB_TABLES..............................')
    logging.info(f"""
    !**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!
    WELCOME TO ONLINE SHOPPING MALL!
    Explore a wide variety of products tailored to your needs.
    Enjoy seamless shopping with secure payments and fast delivery.
    Don't miss out on our exclusive offers and discounts!
    Happy shopping!
    !**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!**!
    """)
    create_db_tables()
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

def get_client() -> Union[MockSupabaseClient, Client]:
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
            client: Union[MockSupabaseClient, Client] = Depends(get_client),
            session: Session = Depends(get_session)
            ):
       
    # Determine the correct table name and model based on the client type
    if isinstance(client, MockSupabaseClient):
        table_name = 'mock_user'
        model = MockUser
    else:
        table_name = 'user'
        model = User
    
  # Check if user already exists
    existing_users = client.table(table_name).select('*').eq('email', payload.email).execute().data
    
    try:
        if existing_users:
            raise HTTPException(status_code=400, detail="EMAIL_ALREADY_IN_USE")

        #  Determine user data source
        user_data = {
            "username": payload.username,
            "email": payload.email,
            "password": payload.password,
            "source": "mock" if isinstance(client, MockSupabaseClient) else "real"  # Set source based on client type
        }
    
        response = client.auth.sign_up(user_data)
        registered_user = response.get('user')
        generated_apikey = response.get('api_key')

        # Save user to the database
        new_user = model(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            api_key=generated_apikey,
            source=user_data["source"]  # Set the source in the database
        )
        session.add(new_user)
        session.commit()

        # Create consumer and key in Kong
        if registered_user and generated_apikey:
            # Pass the username and generated API key to create_consumer_and_key
            kong_response = create_consumer_and_key(registered_user.username, 
                                                    generated_apikey)
            logging.info(f"KONG_CONSUMER_AND_KEY_RESPONSE: {kong_response}")
        else:
            logging.error("USER_REGISTRATION_FAILED_OR_API_KEY_WAS_NOT_GENERATED")


    except Exception as e:
        session.rollback()
        error_message = str(e)
        logging.error(f'ERROR****:{str(e)}')
        raise HTTPException(status_code=400, detail=f'NATURE_OF_ERROR:{error_message}')
   
    user_event_payload= NotifyUser(
        username= payload.username,
        email= payload.email,
        password= payload.password,
        api_key= generated_apikey,
        action = 'Signup'
    )
    logging.info(f'REGISTERED_USER:{registered_user}')
    # USER_SIGNUP_NOTIFICATION
    await notify_user_actions(user_event_payload, producer)
    return registered_user

@app.post("/user/login")
async def login(
                payload: LoginInfo,
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                client: Union[MockSupabaseClient, Client] = Depends(get_client)):
    
    logging.info(f"Received login payload: {payload}")
    response = client.auth.login(payload)
    # Check if login was successful
    if "error" in response:
        logging.error(f'Login failed: {response["error"]}')
        raise HTTPException(status_code=400, detail=response["error"])

    user_data = response.get("user")
    
    # Ensure user_data is not None
    if user_data is None:
        logging.error("User data is None")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # Safely access username and api_key

    extracted_id= user_data.id
    username = user_data.username
    generated_apikey = user_data.api_key
    logging.error(f'RESPONSE_IN_LOGIN: {response}')

    message_payload = NotifyUser(
        action= 'Login',
        id= extracted_id,
        username= username,
        email= payload.email,
        password= payload.password,
        api_key= generated_apikey
        )

    await notify_user_actions(message_payload, producer)
    return message_payload

@app.get("/user/profile")
async def get_user_profile(
        api_key: str = Header(..., alias="apikey"),  # Match the alias to Kong "apikey"
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        client: Union[MockSupabaseClient, Client] = Depends(get_client)
        ):
   
    response = client.auth.user_profile(api_key)
    if response.get("status") == "failed":
        return {"error": response["error"], "status": "failed"}
   
    user = response.get("user")
    if not user:
        return {"error": "User profile not found", "status": "failed"}


    user_message = UserMessage(action="get_user_profile", user=user)
    await notify_user_profile(user_message, producer)
   
    return user_message


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
