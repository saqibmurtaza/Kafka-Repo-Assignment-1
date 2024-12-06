from fastapi import FastAPI, Depends, HTTPException, Header, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from supabase import Client
from typing import Union, Optional
from contextlib import asynccontextmanager
from .dependencies import get_mock_supabase_client, get_supabase_cleint
from .kong_api_calls import create_consumer_and_key, check_kong_consumer
from .database import create_db_tables, get_session
from .mock_user import MockSupabaseClient, get_user_role_by_email
from .producer import get_kafka_producer
from .models import User, MockUser, UserInfo, UserMessage, NotifyUser, LoginInfo
from .settings import settings
from .notify_logic import notify_user_profile, notify_user_actions
from aiokafka import AIOKafkaProducer
import logging, asyncio, json, jwt


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('CREATING_DB_TABLES..............................')
    try:
        create_db_tables()
        logging.info(f'\nTABLES_CREATED_SUCCESSFULLY\n')
    except Exception as e:
        logging.error(f'\nAN_ERROR_OCCURED : {str(e)}...............\n')
    await asyncio.sleep(5)
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
        request: Request,
        admin_secret: Optional[str] = Header(None,alias='admin_key'),
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        client: Union[MockSupabaseClient, Client] = Depends(get_client),
        session: Session = Depends(get_session)
    ):
    logging.info(f"Request headers: {dict(request.headers)}") # display all headers in payload request
    
    if isinstance(client, MockSupabaseClient): # in .env variable set it true
        model = MockUser
    else:
        model = User
    
    # Assgin Roles
    if admin_secret == settings.ADMIN_SECRET:
        role = 'admin'
    else:
        role = 'user'

    try:
        # Prepare user's data for further processing
        user_data = {
            "username": payload.username,
            "email": payload.email,
            "password": payload.password,
            "source": "mock" if isinstance(client, MockSupabaseClient) else "real",
            "role": role
        }

        # Attempt to sign up the user
        response = client.auth.sign_up(user_data)
        
        if "USER_ALREADY_EXIST" in response.get("user", []) or response.get('user', []) == []:
            logging.info(f"USER_WITH_EMAIL__{user_data['email']}__ALREADY_EXISTS")
            raise HTTPException(status_code=409, detail="USER_ALREADY_EXISTS")

        registered_user = response.get('user')
        generated_id = registered_user.id
        generated_apikey= registered_user.api_key

        apikey= None #initialize the key
        # Before generating new API key,check if the consumer already exists in Kong
        try:
            kong_response = check_kong_consumer(registered_user.email)

            if kong_response:
                logging.info(
                    f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
                    f"KONG_CONSUMER_ALREADY_EXISTS_FOR__{registered_user.email}"
                    f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
                    )

                apikey= kong_response.get('auth_key')
                logging.info(
                    f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
                    f'EXISTIING_API_KEY**:{apikey}'
                    f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
                    )
           
           # CREATE_KONG_CONSUMER_AND_KEY
            else:
                # No existing consumer, create a new one
                apikey =  generated_apikey
                kong_response = create_consumer_and_key(registered_user.email, apikey)
                
                if 'id' not in kong_response:
                    logging.error(f"KONG_CONSUMER_REGISTRATION_FAILED_FOR__{registered_user.email}")
                    raise HTTPException(status_code=500, detail="Kong consumer registration failed.")

            logging.info(
                f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
                f"KONG_CONSUMER_CREATED_OR_FOUND_FOR__{registered_user.email}__APIKEY__{apikey}"
                f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
                )

        except Exception as kong_error:
            logging.error(f"KONG_CONSUMER_REGISTRATION_ERROR: {kong_error}")
            raise HTTPException(status_code=500, detail="Kong consumer registration failed.")

        # Save the new user or update with the existing Kong API key
        new_user = model(
            id= generated_id,
            username= payload.username,
            role= role,
            email= payload.email,
            password= payload.password,
            api_key= apikey,  
            source= user_data["source"]
        )
        session.add(new_user)
        session.commit()

        logging.info(
            f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
            f"USER_REGISTERED_IN_DB__{payload.email}__ID__{generated_id}"
            f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
            )
        
        # Prepare data for sending to notification service
        data_instance = NotifyUser(
            id= generated_id,
            username= payload.username,
            role= role,
            email= payload.email,
            password= payload.password,
            api_key= apikey,
            token= None, # login endpoint will generate it, here its none
            action= 'Signup'
        )

        await notify_user_actions(data_instance, producer) # Notify user
        
        logging.info(
            f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
            f"NOTIFICATION_SENT_TO_USER__{registered_user.email}__ROLE__{role}"
            f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
            )
        # Final return if everything succeeds
        return registered_user

    except HTTPException as e:
        logging.error(f"HTTP_EXCEPTION_OCCURRED: {e.detail}")
        raise e

    except Exception as e:
        session.rollback()
        error_message= str(e)
        logging.error(f"UNEXPECTED_ERROR: {e}")
        raise HTTPException(status_code=500, detail=error_message)


@app.post("/user/login")
async def login(
                payload: LoginInfo,
                api_key: str = Header(..., alias='apikey'),
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                client: Union[MockSupabaseClient, Client] = Depends(get_client)):
    
    response = client.auth.login(payload) 
    if "CREDENTIALS_MISMATCHED" in response:
        logging.info(f'LOGIN_FAILED: {response}')
        raise HTTPException(status_code=409, detail='CREDENTIALS_NOT_MATCHED')

    # Extract Data returned by mock_user
    user_data= response.get('user')
    token= response.get('token')
    if token:
        user_data['token'] = token
    else:
        logging.error(f"TOKEN_IS_NOT_RECIEVED_FROM_")
    
    # AUTHENTICATION
    consumer_response= check_kong_consumer(user_data.get('email'))
    logging.info(f'CONSUMER_RESPONSE:{consumer_response}')

    auth_key= consumer_response.get('auth_key')
    logging.info(f'CONSUMER_AUTH_KEY: {auth_key}***')

    if auth_key != api_key:
        logging.error("KONG_AUTHENTICATION_FAILED: key mismatched")
        raise HTTPException(status_code=401, detail="AUTHENTICATION_FAILED")

    logging.info(
        f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
        f'AUTHENTICATION_PROCESS_SUCCESSFUL_WITH_KEY__{auth_key}'
        f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
        )

    # Pass instance of NotifyUser to function, it makes easy when notify function get it
    data_instance= NotifyUser(action= 'login', **user_data)

    await notify_user_actions(data_instance, producer) # Notify user

    message = f'SUCCESSFULLY_LOGGED_IN_WITH__{user_data.get("email")}'
    return {
        "message": message,
        "token": token
        }

@app.get("/user/profile", response_model=User)
async def get_user_profile(
    user_api_key: str = Header(..., alias='apikey'),
    token: str = Header(..., alias='token'),
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    client: Union[MockSupabaseClient, Client] = Depends(get_client)
    ):
    try:
        decoded_token= jwt.decode(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
        logging.info(f"DecodedToken:{decoded_token}")
        
        # Extract email from token; without logging in, you cannot obtain the token and consequently do not have the email for authentication
        email= decoded_token.get('email')
        role= decoded_token.get('role')

        # AUTHENTICATION
        consumer_response= check_kong_consumer(email)
        # Check if consumer_response is None
        if consumer_response is None:
            logging.error(f'NO_CONSUMER_FOUND_WITH_MENTIONED_EMAIL: {email}')
            raise HTTPException(status_code=404, detail=f"No consumer found with email: {email}")
 
        auth_key= consumer_response.get('auth_key')

        if auth_key != user_api_key:
            logging.error("KONG_AUTHENTICATION_FAILED: key mismatched")
            raise HTTPException(status_code=401, detail="AUTHENTICATION_FAILED")

        logging.info(
            f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
            f'AUTHENTICATION_PROCESS_SUCCESSFUL_WITH_KEY__{auth_key}'
            f'!\n****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
            )

        if isinstance(client, MockSupabaseClient):
            try:
                mock_user_profile= client.auth.user_profile(user_api_key)
                if not mock_user_profile:
                    raise HTTPException(status_code=403, detail='API_KEY_NOT_MATCHED')

                # Role-based Access Control
                # role= get_user_role_by_email(email)
                if role == 'admin':
                    # Extract List, recieved from client.auth
                    data_list= []                
                    for my_user in mock_user_profile: 
                        data_obj= User(**my_user) # # Create a User object from the dictionary
                        data_list.append(data_obj) 

                    logging.info(f"DATA_LIST:{data_list}")
                    # Prepare message for Notification & DESCRIBE_ACTION in UserMessage
                    user_message = UserMessage(action="get_user_profile", user=data_list)
                    # FUNCTION_CALL
                    await notify_user_profile(user_message, producer)
                        
                    # Convert the Pydantic model to a dictionary before JSON serialization
                    formatted_mssg_json= json.dumps(user_message.dict(), indent=4) #convert a Python object/dict into a JSON-formatted string
                    return Response(content=formatted_mssg_json, media_type="application/json")
                elif role == 'user':
                    # User: Can only access their own profile <---
                    user_profile = next(
                        (user for user in mock_user_profile if user['email'] == email), None
                    )
                    if not user_profile:
                        raise HTTPException(status_code=404, detail="USER_PROFILE_NOT_FOUND")

                    # Return the user's own profile
                    data_obj = User(**user_profile)
                    logging.info(f"USER_PROFILE: {data_obj}")
                    return data_obj.dict()
    
                # Deny access for other roles <---
                raise HTTPException(status_code=403, detail="ACCESS_DENIED: Role not recognized")
    
            except Exception as e:
                error_message=str(e)
                logging.error(f'ERROR_DETAILS : {str(e)}')
                raise HTTPException(status_code=403, detail=f"NATURE_OF_ERROR:{error_message}")
            
        else: #FOR REAL DB
            try:
                response = client.table('user').select('*').execute()
                real_user_profile = response.data
                if role == 'admin':
                    formatted_json = json.dumps(real_user_profile, indent=4)
                    return formatted_json
                elif role == 'user':
                    user_profile = next(
                        (user for user in real_user_profile if user['email'] == email), None
                    )
                    if not user_profile:
                        raise HTTPException(status_code=404, detail="USER_PROFILE_NOT_FOUND")
                    return user_profile
                else:
                    raise HTTPException(status_code=403, detail="ACCESS_DENIED: Role not recognized")

            except Exception as e:
                error_message=str(e)
                logging.error(f'ERROR_STATUS : {error_message}')
                raise HTTPException(status_code=403, detail=f"NATURE_OF_ERROR:{error_message}")
    
    except Exception as e:
        # Log the actual error message
        logging.error(f"Error occurred: {e}")
        # If the error is an HTTPException, use its status code and detail
        if isinstance(e, HTTPException):
            raise e
        # For all other exceptions, return the actual error message with a 400 status code
        raise HTTPException(status_code=400, detail=str(e))

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
