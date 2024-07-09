from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_db_tables
from .consumer import start_consumer
from contextlib import asynccontextmanager
from fastapi_2 import settings
import asyncio, logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info('creating db tables ...')
    consumer_task= asyncio.create_task(
        start_consumer(
            topic=settings.TOPIC_PRODUCTS_CRUD,
            bootstrapserver=settings.BOOTSTRAP_SERVER,
            consumer_group_id=settings.CONSUMER_GROUP_PRODUCT_MANAGER))
    create_db_tables()
    try:
        yield
    finally:
        consumer_task.cancel()
        await consumer_task
    
app= FastAPI(
    lifespan=lifespan,
    title='API_2 - Consumer & DB operations',
    servers=[
        {
            "url":"http://localhost:8001",
            "description":"Server:Uvicorn, port:8001"
        }
    ]
)

@app.get("/")
async def read_root():
    return {"message":"API_2 - Consumer & DB operations"}

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


# Add any other origins if needed
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

