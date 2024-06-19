import json
from fastapi import FastAPI, Depends, Body
from api_1 import settings
from .models import Product
from .producer import get_kafka_producer, AIOKafkaProducer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

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
async def add_product(product:Product, producer: AIOKafkaProducer=Depends(get_kafka_producer), 
                      topic=settings.TOPIC_PRODUCTS_CRUD) -> Product:
# Serialize the product to a dictionary
    product_dict = product.model_dump()
    product_event= {"operation" : "add", "data" : product_dict}
# Convert the product_event_dictionary to a JSON-encoded string
    product_event_json = json.dumps(product_event).encode('utf-8')
    await producer.send_and_wait(topic, product_event_json )
    print(f'My_Product : {product_dict}')
    print(f'My_Product_Json : {product_event_json}')
    return product

@app.get("/read_product/{id}")
async def read_product(id:int, producer: AIOKafkaProducer=Depends(get_kafka_producer),
                topic=settings.TOPIC_PRODUCTS_CRUD):
    product_event= {"operation" : "read", "data" : {"product_id" : id}}
    product_event_json= json.dumps(product_event).encode('utf-8')
    await producer.send_and_wait(topic, product_event_json)
    return {"message" : "product read request sent"}

@app.delete("/delete_product/{id}")
async def delete_product(id:int, producer:AIOKafkaProducer=Depends(get_kafka_producer),
                         topic=settings.TOPIC_PRODUCTS_CRUD):
    product_event= {"operation" : "delete", "data" : {"product_id": id}}
    product_event_json = json.dumps(product_event).encode('utf-8')
    await producer.send_and_wait(topic, product_event_json)
    return {"message" : "product delete request sent"}

class ProductUpdate(BaseModel):
    product_name: str
    description: str
    price: float

@app.put("/update_product/{id}")
async def update_product_endpoint(
    id: int,
    updates: ProductUpdate,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    topic: str = settings.TOPIC_PRODUCTS_CRUD  # Corrected typo and added topic parameter
):
    product_event = {
        "operation": "update",
        "data": {
            "product_id": id,
            **updates.dict()  # Flatten the updates into the data dictionary
        }
    }
    product_event_json = json.dumps(product_event).encode('utf-8')  # Corrected encoding typo
    await producer.send_and_wait(topic, product_event_json)
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
