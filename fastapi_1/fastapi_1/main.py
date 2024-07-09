from fastapi import FastAPI, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi_1 import settings
from .models import Product
from .producer import get_kafka_producer, AIOKafkaProducer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from fastapi_1.product_pb2 import Product as ProductProto, ProductEvent
import sys, os, logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

app = FastAPI(
    title= 'API_1 - Producer & CRUD Endpoints',
    servers=[
        {
        "url": "http://localhost:8000",
        "description": "Server:Uvicorn, port:8000"
        }]
    )

@app.get("/")
async def read_root():
    return {"Project":"API-1 - Producer & CRUD Endpoints"}

@app.post("/add_product", response_model=Product)
async def add_product(product: Product, producer: AIOKafkaProducer = Depends(get_kafka_producer), 
                      topic: str = settings.TOPIC_PRODUCTS_CRUD) -> Product:
    product_proto = ProductProto(
        id=product.id,
        product_name=product.product_name,
        description=product.description,
        price=product.price
    )
    product_event_proto = ProductEvent(operation="add", data=product_proto)
    product_event_bytes = product_event_proto.SerializeToString()
    await producer.send_and_wait(topic, product_event_bytes)
    print(f'My_Product: {product}')
    print(f'My_Product_Bytes: {product_event_bytes}')
    return product

@app.get("/read_product/{id}")
async def read_product(id: int, producer: AIOKafkaProducer = Depends(get_kafka_producer),
                       topic: str = settings.TOPIC_PRODUCTS_CRUD):
    # Create a Protobuf message for the product event
    product_event_proto = ProductEvent(operation="read", data=ProductProto(id=id))
    # Serialize the Protobuf message to bytes
    product_event_bytes = product_event_proto.SerializeToString()
    # Send the serialized bytes
    await producer.send_and_wait(topic, product_event_bytes)
    return {"message": "product read request sent"}

@app.delete("/delete_product/{id}")
async def delete_product(id: int, producer: AIOKafkaProducer = Depends(get_kafka_producer),
                         topic: str = settings.TOPIC_PRODUCTS_CRUD):
    # Create a Protobuf message for the product event
    product_event_proto = ProductEvent(operation="delete", data=ProductProto(id=id))
    # Serialize the Protobuf message to bytes
    product_event_bytes = product_event_proto.SerializeToString()
    # Send the serialized bytes
    await producer.send_and_wait(topic, product_event_bytes)
    return {"message": "product delete request sent"}

class DeleteProductsRequest(BaseModel):
    ids: List[int]

@app.delete("/delete_multiple_products")
async def delete_products(request: DeleteProductsRequest, producer: AIOKafkaProducer = Depends(get_kafka_producer),
                          topic: str = settings.TOPIC_PRODUCTS_CRUD):
    for id in request.ids:
        product_event_proto = ProductEvent(operation="delete", data=ProductProto(id=id))
        product_event_bytes = product_event_proto.SerializeToString()
        await producer.send_and_wait(topic, product_event_bytes)
        logger.info(f"Sent delete request for product id: {id}")
    return {"message": "delete requests sent for products"}


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

@app.put("/update_product/{id}")
async def update_product_endpoint(
        id: int,
        updates: ProductUpdate,
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        topic: str = settings.TOPIC_PRODUCTS_CRUD):
    # Create a Protobuf message for the product with updated fields
    product_proto = ProductProto(
        id=id,
        product_name=updates.product_name,
        description=updates.description,
        price=updates.price
    )
    # Create a Protobuf message for the product event
    product_event_proto = ProductEvent(operation="update", data=product_proto)
    # Serialize the Protobuf message to bytes
    product_event_bytes = product_event_proto.SerializeToString()
    # Send the serialized bytes
    await producer.send_and_wait(topic, product_event_bytes)
    return {"message": "product update request sent"}

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