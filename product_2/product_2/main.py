from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from urllib.parse import unquote
from .database import create_db_tables, get_session, supabase
from .consumer import start_consumer
from contextlib import asynccontextmanager
from .settings import settings
from .auth_handler import AuthMiddleware
import asyncio, logging, json

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info('CREATING DB TABLES ......')
    consumer_task= asyncio.create_task(
        start_consumer(
            topic=settings.TOPIC_PRODUCT_CRUD,
            bootstrap_server=settings.BOOTSTRAP_SERVER,
            consumer_group_id=settings.CONSUMER_GROUP_PRODUCT_MANAGER))
    create_db_tables()
    logging.info('TABLES_CREATED_SUCCESSFULLY')
    try:
        yield
    finally:
        consumer_task.cancel()
        await consumer_task
    
app= FastAPI(
    lifespan=lifespan,
    title='SaqibShopSphere _ Consumer & DB operations',
    servers=[
        {
            "url":"http://localhost:8007",
            "description":"Server:Uvicorn, port:8007"
        }
    ]
)

# Add the authentication middleware globally
app.add_middleware(AuthMiddleware)

@app.get("/")
async def read_root():
    return {"message":"Online Mart Catalogue - Consumer & DB operations"}

@app.get("/api/product/{product_name}")
async def search_product(product_name:str): # Ensure this is the exact name you expect
        
    try:
        logging.info(f"RCD PARAMETER:{product_name}")
        # Decode and trim the product_name parameter to handle URL-encoded spaces
        decoded_product_name = unquote(product_name).strip()
        logging.info(f"Decoded and Trimmed Product Name: {decoded_product_name}")

        response= supabase.from_('catalogue').select('*').eq('product_name', decoded_product_name).execute()
        logging.info(f"RAW DATA:{response}")
        response_dict= response.json()
        logging.info(f"RESPONSE_JSON:{response_dict}")

        if isinstance(response_dict, str):
            response_dict= json.loads(response_dict)
            logging.info(f"RESPONSE_DICT:{response_dict}")

        products= []
        for my_name in response_dict['data']:  # Access the 'data' key directly
            if my_name['product_name'].strip().lower() == decoded_product_name.lower():  # Access the 'product_name' key in the dictionary
                products.append(my_name)
        logging.info(f"Filtered Products List: {products}")
        return products
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

origins = [
#HTTP
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",

    "http://localhost:8006",
    "http://127.0.0.1:8006",
    "http://localhost:8007",
    "http://127.0.0.1:8007",
    "http://localhost:8008",
    "http://127.0.0.1:8008",
    "http://localhost:8009",
    "http://127.0.0.1:8009",
    "http://localhost:8010",
    "http://127.0.0.1:8010",
    "http://localhost:8011",
    "http://127.0.0.1:8011",

    "http://localhost:8080",
    "http://127.0.0.1:8080",
#HTTPS    
    "https://localhost:8000",
    "https://127.0.0.1:8000",
    "https://localhost:8001",
    "https://127.0.0.1:8001",
    
    "https://localhost:8006",
    "https://127.0.0.1:8006",
    "https://localhost:8007",
    "https://127.0.0.1:8007",
    "https://localhost:8008",
    "https://127.0.0.1:8008",
    "https://localhost:8009",
    "https://127.0.0.1:8009",
    "https://localhost:8010",
    "https://127.0.0.1:8010",
    "https://localhost:8011",
    "https://127.0.0.1:8011",
    
    "https://localhost:8080",  
    "https://127.0.0.1:8080", 


# Add any other origins if needed
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

