from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from contextlib import asynccontextmanager
from .model import Inventory, InventoryResponse, InventoryCreate
from .dependencies import get_mock_inventory, get_real_inventory
from .producer import get_kafka_producer
from .mock_inv_service import MockInventoryService
from .settings import settings
import logging, json, asyncio

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

app = FastAPI(
    
    title= 'ShopSphere _ Inventory Service',
    servers=[
        {
        "url": "http://localhost:8011",
        "description": "Server:Uvicorn, port:8011"
        }]
    )

def get_inventory_service():
    if settings.MOCK_SUPABASE:
        return get_mock_inventory()
    return get_real_inventory

@app.get("/")
async def read_root():
    return {"message" : "Inventory Service with Kafka"}

@app.post("/inventory", response_model=InventoryResponse)
async def create_inventory(inventory: InventoryCreate,
                           producer: AIOKafkaProducer = Depends(get_kafka_producer),
                           service: MockInventoryService = Depends(get_inventory_service)):
    
    response = inventory.model_dump()  # Convert pydantic model instance to dict
    created_inventory = service.create_inventory(response)

    # Serialize the dictionary to a JSON string before sending
    response_json = json.dumps(response).encode('utf-8')
    await producer.send_and_wait(settings.TOPIC_INVENTORY_UPDATES, response_json)
    logging.info(f'STOCK-CREATED :{created_inventory}')
    
    # Send notification if inventory is low
    if created_inventory['quantity'] <= created_inventory['threshold']:
        notification_payload = {
            "item_name": created_inventory['item_name'],
            "quantity": created_inventory['quantity'],
            "threshold": created_inventory['threshold'],
            "email": created_inventory['email']
        }
        notification_json = json.dumps(notification_payload).encode('utf-8')
        await producer.send_and_wait(settings.TOPIC_INVENTORY_UPDATES, notification_json)
        logging.info(f'LOW_STOCK_NOTIFICATION_SENT : {notification_payload}')
    
    return created_inventory

@app.get("/inventory/{item_id}", response_model=InventoryResponse)
async def track_inventory(item_id: int,
                          producer: AIOKafkaProducer = Depends(get_kafka_producer),
                          service: MockInventoryService = Depends(get_inventory_service)):
    tracked_inventory = service.track_inventory(item_id)
    logging.info(f'STOCK_ITEM_TRACKED : {tracked_inventory}')
    
    if tracked_inventory:
        tracked_inv_json = json.dumps(tracked_inventory).encode('utf-8')
        await producer.send_and_wait(settings.TOPIC_INVENTORY_UPDATES, tracked_inv_json)
        
        # Send notification if inventory is low
        if tracked_inventory['quantity'] <= tracked_inventory['threshold']:
            notification_payload = {
                "item_name": tracked_inventory['item_name'],
                "quantity": tracked_inventory['quantity'],
                "threshold": tracked_inventory['threshold'],
                "email": tracked_inventory['email']
            }
            notification_json = json.dumps(notification_payload).encode('utf-8')
            await producer.send_and_wait(settings.TOPIC_INVENTORY_UPDATES, notification_json)
            logging.info(f'LOW_STOCK_NOTIFICATION_SENT : {notification_payload}')
        
        return tracked_inventory
    raise HTTPException(status_code=404, detail='Item not found in Inventory')

@app.put("/inventory/{item_id}", response_model=InventoryResponse)
async def update_inventory(item_id: int,
                           update_data: InventoryCreate,
                           producer: AIOKafkaProducer = Depends(get_kafka_producer),
                           service: MockInventoryService = Depends(get_inventory_service)):
    
    update_data = {k: v for k, v in update_data.model_dump().items() if k != 'id'}
    updated_stock = service.update_inventory(item_id, update_data)
    logging.info(f'STOCK_UPDATED : {updated_stock}')
    
    if updated_stock:
        updated_stock_json = json.dumps(update_data).encode('utf-8')
        await producer.send_and_wait(settings.TOPIC_INVENTORY_UPDATES, updated_stock_json)
        
        # Send notification if inventory is low
        if updated_stock['quantity'] <= updated_stock['threshold']:
            notification_payload = {
                "item_name": updated_stock['item_name'],
                "quantity": updated_stock['quantity'],
                "threshold": updated_stock['threshold'],
                "email": updated_stock['email']
            }
            notification_json = json.dumps(notification_payload).encode('utf-8')
            await producer.send_and_wait(settings.TOPIC_INVENTORY_UPDATES, notification_json)
            logging.info(f'LOW_STOCK_NOTIFICATION_SENT : {notification_payload}')
        
        return updated_stock
    raise HTTPException(status_code=404, detail='Item not found in Inventory')

@app.delete("/inventory/{item_id}", response_model=InventoryResponse)
async def delete_inventory(item_id: int,
                           producer: AIOKafkaProducer = Depends(get_kafka_producer),
                           service: MockInventoryService = Depends(get_inventory_service)):
    
    deleted_stock = service.delete_inventory(item_id)
    logging.info(f'STOCK_TO_BE_DELETED : {deleted_stock}')
    
    if deleted_stock:
        deleted_stock_json = json.dumps(deleted_stock).encode('utf-8')
        await producer.send_and_wait(settings.TOPIC_INVENTORY_UPDATES, deleted_stock_json)
        return deleted_stock
    raise HTTPException(status_code=404, detail='ITEM_NOT_FOUND')





























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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

