from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .settings import settings
from .consumer import start_consumer
from .database import create_db_tables, supabase
from .models import Inventory, InventoryUpdate, InventoryCreate, UpdateStock
from .producer import get_kafka_producer, AIOKafkaProducer
from .inventory_pb2 import Inventory as InvProto, InventoryUpdates as InvMessage
from .fetched_from_db import fetch_data
from urllib.parse import unquote
from .auth_handler import AuthMiddleware
import logging, asyncio, json, jwt

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    logging.info('CREATING_DB_TABLES................____________..')
    try:
        create_db_tables()
        logging.info(f'\nTABLES_CREATED_SUCCESSFULLY\n')
    except Exception as e:
        logging.error(f'\nAN_ERROR_OCCURED_IN_CONTEXT_MANAGER : {str(e)}...............\n')
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

# Add the authentication middleware globally
app.add_middleware(AuthMiddleware)

@app.get("/")
async def read_root():
    return {"Project":"API-1 - Producer & CRUD Endpoints"}


@app.post("/inventory", response_model=Inventory)
async def create_inventory(
                payload: InventoryCreate,
                producer: AIOKafkaProducer = Depends(get_kafka_producer), 
                topic: str = settings.TOPIC_INVENTORY_UPDATES
                ) -> Inventory:
    
    # Fetched data from product_2 service
    catalogue_product= fetch_data(payload.id)
    logging.info(f"catalogue product : {catalogue_product}")

    if not catalogue_product:
        logging.warning(f"PRODUCNT_ID_{payload.id}_NOT_FOUND_IN_CATALOGUE")
        raise HTTPException(status_code=404, detail=f"PRODUCNT_ID_{payload.id}_NOT_FOUND_IN_CATALOGUE")

    item_name= catalogue_product['product_name']
    unit_price= catalogue_product['price']
    description= catalogue_product['description']

    inventory_data = InvProto(
        id=None,
        item_name= item_name,
        unit_price= unit_price,
        description= description,
        stock_in_hand= payload.stock_in_hand,
        threshold= payload.threshold,
        email= payload.email
    )
    logging.info(f'inv data: {inventory_data}')
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

@app.get("/api/inventory/{item_name}")
async def track_inventory(
    item_name:str
    ):
    decoded_product_name = unquote(item_name).strip()
    
    response= supabase.from_('inventory').select('*').eq('item_name', decoded_product_name).execute()
    response_dict= response.json() # convert to str or dict
    if isinstance(response_dict, str): # check if it be str then use json.loads to convert it to dict
        response_dict= json.loads(response_dict)

        inventory_list= []
        for my_inventory in response_dict['data']:
            if my_inventory['item_name'].strip().lower() == item_name.lower():
                inventory_list.append(my_inventory)
        return inventory_list

@app.put("/api/inventory/{item_name}")
async def update_stock(item_name: str, payload: UpdateStock):
    decoded_item_name = unquote(item_name).strip()

    # Fetch current inventory for the item to ensure that the item existence
    response = supabase.from_("inventory").select("*").eq("item_name", decoded_item_name).execute()

    update_data= payload.dict()
    # Handle response and update stock in the database
    if response.data:
        updated_response = supabase.from_("inventory").update(update_data).eq("item_name", decoded_item_name).execute()
        return {"message": "Stock updated successfully.", "new_stock": payload}
    else:
        raise HTTPException(status_code=404, detail="Item not found.")

@app.get("/inventory/{id}")
async def track_inventory(
                id: str, 
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                topic: str = settings.TOPIC_INVENTORY_UPDATES
                ):
    # Create an instance of InvMessage(proto_schema)
    msg_response = InvMessage(operation="read", data=InvProto(id=id))
    # Serialize the Protobuf message to bytes
    msg_response_bytes = msg_response.SerializeToString()
    
    # Send the serialized bytes
    await producer.send_and_wait(topic, msg_response_bytes)
    return {"MESSAGE": f"REQUEST_SENT_TO_CONSUMER_TO_EXTRACT_INVENTORY_FROM_DB_OF_ID : {id}"}

@app.put("/inventory/{id}")
async def update_inventory(
        id: str,
        payload: InventoryUpdate,
        request: Request,  # We need to access headers directly from the request
        producer: AIOKafkaProducer = Depends(get_kafka_producer),
        topic: str = settings.TOPIC_INVENTORY_UPDATES
        ):

    # Middleware will have already decoded the token and added the email to the request context
    email = request.state.email  # the middleware adds the decoded email to the request state
    apikey= request.state.apikey
    logging.info(f"EXTRACTED_EMAIL-FROM_TOKEN: {email}")

    """
    You no longer need to validate API key or fetch user details 
    from the user service after using authentication middleware globally
    """
    payload_authkey = request.headers.get("apikey")
    """
    request.headers.get("apikey") -- extracted from headers (sent by client)
    request.state.api_key -- This is the API key stored in the 
    request.state object (typically set in middleware after 
    processing and validation)
    """
    if payload_authkey == request.state.apikey and request.state.role == 'admin':  # Middleware should set these values
        # Create a Protobuf message for the inv with updated fields
        inv_data = InvProto(
            id=id,
            item_name= payload.item_name,
            unit_price= payload.unit_price,
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
    return {f'MESSAGE: REQUEST_SENT_TO_CONSUMER_TO_UPDATE_INVENTORY_IN_DB_OF_ID :{id}'}

@app.delete("/inventory/{id}")
async def delete_inventory(
                id: str,
                request: Request,
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                topic: str = settings.TOPIC_INVENTORY_UPDATES
                ):
    
    payload_authkey= request.headers.get('apikey')
    fetched_apikey= request.state.apikey
    role= request.state.role

    if payload_authkey == fetched_apikey and role:

        # Create an instance of InvMessage
        msg_response = InvMessage(operation="delete", 
                                        data=InvProto(id=id))
        # Serialize the Protobuf message to bytes
        msg_response_bytes = msg_response.SerializeToString()
        
        # Send the serialized bytes
        await producer.send_and_wait(topic, msg_response_bytes)
        return {f'MESSAGE: REQEUST_SENT_TO_DELETE_INVENTORY_FROM_DB_OF_ID :{id}'}
    
    logging.info(f'AUTH_KEY_MISMATCHED : {payload_authkey}')

@app.get("/inventory")
async def view_inventory(
                producer: AIOKafkaProducer = Depends(get_kafka_producer),
                topic: str = settings.TOPIC_INVENTORY_UPDATES
                ):
    # InvProto() creates an empty instacne, which act as placeholder
    msg_response = InvMessage(operation="list", data=InvProto())
    # Serialize the Protobuf message to bytes
    msg_response_bytes = msg_response.SerializeToString()
    # Send the serialized bytes
    
    await producer.send_and_wait(topic, msg_response_bytes)
    return {"MESSAGE": "REQUEST_SENT_TO_CONSUMER_TO_GET_INVENTORY_LIST_FROM_DB"}



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