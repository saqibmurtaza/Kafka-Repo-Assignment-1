from fastapi import FastAPI, Depends, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
from .settings import settings
from .models import Product, ProductUpdate, ProductCreate
from .producer import get_kafka_producer, AIOKafkaProducer
from fastapi.middleware.cors import CORSMiddleware
from product_1.product_pb2 import Product as ProductProto, ProductEvent as MessageProto
from .auth_handler import AuthMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

app = FastAPI(
    title= 'Online Shopping Mart Catalogue_ Producer & API Endpoints',
    servers=[
        {
        "url": "http://localhost:8006",
        "description": "Server:Uvicorn, port:8006"
        }]
    )

# Add the authentication middleware globally
app.add_middleware(AuthMiddleware)

@app.get("/")
async def read_root():
    return {"Project":"Online Mart Catalogue - Producer & CRUD Endpoints"}

# CART FUNCTIONALITY
@app.post("/product", response_model=Product)
async def create_catalogue(
                payload: ProductCreate,
                producer: AIOKafkaProducer = Depends(get_kafka_producer), 
                topic: str = settings.TOPIC_PRODUCT_CRUD
                ) -> Product:
    try:
         # Create a Product instance without an ID
        product = Product(
            product_name= payload.product_name,
            description= payload.description,
            price= payload.price,
            quantity= payload.quantity
        )
        product_data = ProductProto(
            id=0,
            product_name= product.product_name,
            description= product.description,
            price= product.price,
            quantity= product.quantity
        )
        msg_response = MessageProto(operation="add", data=product_data)
        msg_response_bytes = msg_response.SerializeToString()
        await producer.send_and_wait(topic, msg_response_bytes)
        return product

    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/product/{id}")
async def track_catalogue_item(
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

@app.put("/product/{id}")
async def update_catalogue_item(
        id: int,
        payload: ProductUpdate,
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        topic: str = settings.TOPIC_PRODUCT_CRUD
        ):
        # Create a Protobuf message for the product with updated fields
        product_proto = ProductProto(
            id=id,
            product_name=payload.product_name,
            description=payload.description,
            price=payload.price,
            quantity=payload.quantity
        )
        # Create a Protobuf message for the product event
        product_event_proto = MessageProto(operation="update", data=product_proto)
        # Serialize the Protobuf message to bytes
        product_event_bytes = product_event_proto.SerializeToString()
        # Send the serialized bytes
        await producer.send_and_wait(topic, product_event_bytes)
        return {f'MESSAGE: REQUEST_SENT_TO_UPDATE_PRODUCT_IN_DB_OF_ID :{id}'}
        
@app.delete("/product/{id}")
async def delete_catalogue_item(
                id: int,
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                topic: str = settings.TOPIC_PRODUCT_CRUD
                ):

    # creates an instance of MessageProto 
    msg_response = MessageProto(operation="delete", 
                                    data=ProductProto(id=id))
    # Serialize the Protobuf message to bytes
    msg_response_bytes = msg_response.SerializeToString()
    # Send the serialized bytes
    await producer.send_and_wait(topic, msg_response_bytes)
    
    return {f'MESSAGE: REQEUST_SENT_TO_DELETE_PRODUCT_FROM_DB_OF_ID :{id}'}


@app.get("/product")
async def view_catalogue(
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