from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
from .settings import settings
from .consumer import start_consumer
from .database import create_db_tables
from .models import Inventory, InventoryUpdate
from .producer import get_kafka_producer, AIOKafkaProducer
from .validation_logic import validate_api_key
from .inventory_pb2 import Inventory as InvProto, InventoryUpdates as InvMessage
import logging, asyncio

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info('CREATING_DB_TABLES................____________..')
    try:
        create_db_tables()
        logging.info(f'\nTABLES_CREATED_SUCCESSFULLY\n')
    except Exception as e:
        logging.error(f'\nAN_ERROR_OCCURED : {str(e)}...............\n')
    await asyncio.sleep(5)
    consumer_task_inv= asyncio.create_task(
        start_consumer(
            topic=settings.TOPIC_INVENTORY_UPDATES,
            bootstrap_server=settings.BOOTSTRAP_SERVER,
            consumer_group_id=settings.CONSUMER_GROUP_INV_MANAGER))

    consumer_task_notify = asyncio.create_task(
        start_consumer(
            topic=settings.TOPIC_NOTIFY_INVENTORY,
            bootstrap_server=settings.BOOTSTRAP_SERVER,
            consumer_group_id=settings.CONSUMER_GROUP_NOTIFY_MANAGER
        )
    )
    create_db_tables()
    try:
        yield
    finally:
        consumer_task_inv.cancel()
        await consumer_task_inv
        consumer_task_notify.cancel()
        await consumer_task_notify

app = FastAPI(
    lifespan=lifespan,
    title= 'INVENTORY SERVICE WITH KAFKA PRODUCER & CONSUMER',
    servers=[
        {
        "url": "http://localhost:8011",
        "description": "Server:Uvicorn, port:8011"
        }]
    )

@app.get("/")
async def read_root():
    return {"Project":"API-1 - Producer & CRUD Endpoints"}


@app.post("/inventory", response_model=Inventory)
async def create_inventory(
                payload: Inventory, 
                producer: AIOKafkaProducer = Depends(get_kafka_producer), 
                topic: str = settings.TOPIC_INVENTORY_UPDATES
                ) -> Inventory:

# Create a Inventory instance without an ID
    inv_instance = Inventory(
        id= 0,
        item_name= payload.item_name,
        descripton= payload.description,
        unit_price= payload.unit_price,
        quantity= payload.quantity,
        stock_in_hand= payload.stock_in_hand,
        threshold= payload.threshold,
        email= payload.email
    )
    inventory_data = InvProto(
        id=0,
        item_name= inv_instance.item_name,
        unit_price= inv_instance.unit_price,
        quantity= inv_instance.quantity,
        stock_in_hand= inv_instance.stock_in_hand,
        threshold= inv_instance.threshold,
        description= inv_instance.description,
        email= inv_instance.email
    )
    msg_response = InvMessage(operation="add", data=inventory_data)
    msg_response_bytes = msg_response.SerializeToString()
# FUNCTION_CALL
    await producer.send_and_wait(topic, msg_response_bytes)
    logging.info(
        f'\n!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
        f'MESSAGE_SENT_SUCCESSFULLY_TO_TOPIC_INVENTORY_UPDATES :\n {inventory_data}\n'
        f'\n!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
        )
    return inventory_data

@app.get("/inventory/{id}")
async def track_inventory(
                id: int, 
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                topic: str = settings.TOPIC_INVENTORY_UPDATES
                ):
    # Create an instance of InvMessage(proto_schema)
    msg_response = InvMessage(operation="read", data=InvProto(id=id))
    # Serialize the Protobuf message to bytes
    msg_response_bytes = msg_response.SerializeToString()
    
    # Send the serialized bytes
    await producer.send_and_wait(topic, msg_response_bytes)
    return {"MESSAGE": f"REQUEST_SENT_TO_EXTRACT_INVENTORY_FROM_DB_OF_ID : {id}"}

@app.delete("/inventory/{id}")
async def delete_inventory(
                id: int,
                payload_authkey: str = Header(..., alias="apikey"),
                email: str = Header(...),
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                topic: str = settings.TOPIC_INVENTORY_UPDATES
                ):
    # Kong_Validation
    try:
        get_user= validate_api_key(payload_authkey, email)
        fetched_apikey= get_user.get('api_key')
    except Exception as e:
        logging.error(f'ERROR***{str(e)}')
        raise HTTPException(status_code=401, detail= 'UNAUHORIZED-CHECK_CREDENTIALS')
    
    if payload_authkey == fetched_apikey:

        # Create an instance of InvMessage
        msg_response = InvMessage(operation="delete", 
                                        data=InvProto(id=id))
        # Serialize the Protobuf message to bytes
        msg_response_bytes = msg_response.SerializeToString()
        
        # Send the serialized bytes
        await producer.send_and_wait(topic, msg_response_bytes)
        return {f'MESSAGE: REQEUST_SENT_TO_DELETE_INVENTORY_FROM_DB_OF_ID :{id}'}
    
    logging.info(f'AUTH_KEY_MISMATCHED : {payload_authkey}')

@app.put("/inventory/{id}")
async def update_inventory(
        id: int,
        payload: InventoryUpdate,
        payload_authkey: str = Header(..., alias="apikey"),
        email: str = Header(...),
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        topic: str = settings.TOPIC_INVENTORY_UPDATES
        ):
# KONG_AUTHENTICATION
    try:
        get_user= validate_api_key(payload_authkey, email)
        fetched_apikey= get_user.get('api_key')
        logging.info(
            f'\n!***!!!***!!!***!!!***!!!***!!!***!!!***!!!***!!!***!!\n'
            f'KONG_AUTHENTICATION_SUCCEEDED\n'
            f'AUTH_KEY : {fetched_apikey}\n'
            f'\n!***!!!***!!!***!!!***!!!***!!!***!!!***!!!***!!!***!!\n'
            )
    except Exception as e:
        logging.error(f'ERROR***{str(e)}')
        raise HTTPException(status_code=401, detail= 'UNAUHORIZED-CHECK_CREDENTIALS')
    
    if payload_authkey == fetched_apikey:
        # Create a Protobuf message for the inv with updated fields
        inv_data = InvProto(
            id=id,
            item_name= payload.item_name,
            unit_price= payload.unit_price,
            quantity= payload.quantity,
            stock_in_hand= payload.stock_in_hand,
            threshold= payload.threshold,
            description= payload.description,
            email= payload.email
        )
        # creates an instance of InvMessage
        msg_response = InvMessage(operation="update", data=inv_data)
        # Serialize the Protobuf message to bytes
        msg_response_bytes= msg_response.SerializeToString() # it populate the instance of InvMessage
        
# FUNCTION_CALL
        await producer.send_and_wait(topic, msg_response_bytes)
        return {f'MESSAGE: REQUEST_SENT_TO_UPDATE_INVENTORY_IN_DB_OF_ID :{id}'}
    logging.info(f'AUTH_KEY_MISMATCHED : {payload_authkey}')

@app.get("/inventory")
async def list_of_inventory(
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                topic: str = settings.TOPIC_INVENTORY_UPDATES
                ):
    # InvProto() creates an empty instacne, which act as placeholder
    msg_response = InvMessage(operation="list", data=InvProto())
    # Serialize the Protobuf message to bytes
    msg_response_bytes = msg_response.SerializeToString()
    # Send the serialized bytes
    
    await producer.send_and_wait(topic, msg_response_bytes)
    return {"MESSAGE": "REQUEST_SENT_TO_GET_LIST_OF_INVENTORY_FROM_DB"}



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