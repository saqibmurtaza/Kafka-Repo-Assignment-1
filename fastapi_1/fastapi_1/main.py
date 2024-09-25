from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
from .settings import settings
from .models import Product, ProductUpdate, ProductCreate
from .producer import get_kafka_producer, AIOKafkaProducer
from .validation_logic import validate_api_key
from fastapi.middleware.cors import CORSMiddleware
from fastapi_1.product_pb2 import Product as ProductProto, ProductEvent as MessageProto
import logging, secrets, uuid

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

app = FastAPI(
    title= 'ShopSphere _ Producer & API Endpoints',
    servers=[
        {
        "url": "http://localhost:8006",
        "description": "Server:Uvicorn, port:8006"
        }]
    )
def generate_api_key():
    return secrets.token_hex(16)
generated_apikey= generate_api_key()

@app.get("/")
async def read_root():
    return {"Project":"API-1 - Producer & CRUD Endpoints"}


@app.post("/product", response_model=Product)
async def create_product(
                payload: ProductCreate, 
                producer: AIOKafkaProducer = Depends(get_kafka_producer), 
                topic: str = settings.TOPIC_PRODUCT_CRUD
                ) -> Product:

# Create a Product instance without an ID
    product = Product(
        product_name= payload.product_name,
        description= payload.description,
        price= payload.price,
    )
    product_data = ProductProto(
        id=0,
        product_name= product.product_name,
        description= product.description,
        price= product.price,
    )
    msg_response = MessageProto(operation="add", data=product_data)
    msg_response_bytes = msg_response.SerializeToString()
    await producer.send_and_wait(topic, msg_response_bytes)
    return product

@app.get("/product/{id}")
async def read_product(
                id: int, 
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                topic: str = settings.TOPIC_PRODUCT_CRUD
                ):
    # Create a Protobuf message for the product event
    msg_response = MessageProto(operation="read", data=ProductProto(id=id))
    # Serialize the Protobuf message to bytes
    msg_response_bytes = msg_response.SerializeToString()
    # Send the serialized bytes
    await producer.send_and_wait(topic, msg_response_bytes)
    return {"MESSAGE": f"REQUEST_SENT_TO_EXTRACT_PRODUCT_FROM_DB_OF_ID : {id}"}

@app.delete("/product/{id}")
async def delete_product(
                id: int,
                payload_authkey: str = Header(..., alias="apikey"),
                email: str = Header(...),
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                topic: str = settings.TOPIC_PRODUCT_CRUD
                ):
    # Kong_Validation
    try:
        get_user= validate_api_key(payload_authkey, email)
        fetched_apikey= get_user.get('api_key')
    except Exception as e:
        logging.error(f'ERROR***{str(e)}')
        raise HTTPException(status_code=401, detail= 'UNAUHORIZED-CHECK_CREDENTIALS')
    
    if payload_authkey == fetched_apikey:

        # creates an instance of MessageProto 
        msg_response = MessageProto(operation="delete", 
                                        data=ProductProto(id=id))
        # Serialize the Protobuf message to bytes
        msg_response_bytes = msg_response.SerializeToString()
        # Send the serialized bytes
        await producer.send_and_wait(topic, msg_response_bytes)
        return {f'MESSAGE: REQEUST_SENT_TO_DELETE_PRODUCT_FROM_DB_OF_ID :{id}'}
    
    logging.info(f'AUTH_KEY_MISMATCHED : {payload_authkey}')

@app.put("/product/{id}")
async def update_product(
        id: int,
        payload: ProductUpdate,
        payload_authkey: str = Header(..., alias="apikey"),
        email: str = Header(...),
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        topic: str = settings.TOPIC_PRODUCT_CRUD
        ):
    # Kong_Validation
    try:
        get_user= validate_api_key(payload_authkey, email)
        fetched_apikey= get_user.get('api_key')
    except Exception as e:
        logging.error(f'ERROR***{str(e)}')
        raise HTTPException(status_code=401, detail= 'UNAUHORIZED-CHECK_CREDENTIALS')
    
    if payload_authkey == fetched_apikey:
        # Create a Protobuf message for the product with updated fields
        product_proto = ProductProto(
            id=id,
            product_name=payload.product_name,
            description=payload.description,
            price=payload.price
        )
        # Create a Protobuf message for the product event
        product_event_proto = MessageProto(operation="update", data=product_proto)
        # Serialize the Protobuf message to bytes
        product_event_bytes = product_event_proto.SerializeToString()
        # Send the serialized bytes
        await producer.send_and_wait(topic, product_event_bytes)
        return {f'MESSAGE: REQUEST_SENT_TO_UPDATE_PRODUCT_IN_DB_OF_ID :{id}'}
        

@app.get("/product")
async def list_of_products(
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                topic: str = settings.TOPIC_PRODUCT_CRUD
                ):
    # Create a Protobuf message for requesting all products
    product_event_proto = MessageProto(operation="list", data=ProductProto())
    # Serialize the Protobuf message to bytes
    product_event_bytes = product_event_proto.SerializeToString()
    # Send the serialized bytes
    await producer.send_and_wait(topic, product_event_bytes)
    return {"MESSAGE": "REQUEST_SENT_TO_GET_LIST_OF_PRODUCTS_FROM_DB"}



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