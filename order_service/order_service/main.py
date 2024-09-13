from fastapi import FastAPI, Depends, HTTPException, Response, Header
from sqlmodel import Session
from contextlib import asynccontextmanager
from typing import List, Union
from supabase import Client
from aiokafka import AIOKafkaProducer
from .notify_logic import send_order_status_notification
from .producer import get_kafka_producer
from .mock_order import MockOrderService, generate_unique_id, generate_api_key
from .database import create_db_tables, get_session
from .dependencies import get_mock_order_service, get_real_order_service, create_consumer_and_api_key
from .models import Order, OrderCreated, MockOrder
from .validation_logic import validate_api_key
from .settings import settings
import logging, asyncio, json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('CREATING_TABLES...................................')
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
    title='ONLINE_SHOPPING_MALL _ ORDER_SERVICE',
    servers=[
        {
            "url": "http://localhost:8010",
            "description": "Server:Uvicorn, port:8010"
        }
    ]
)

def get_client() -> Union[MockOrderService, Client]:
    if settings.MOCK_SUPABASE:
        return get_mock_order_service()
    return get_real_order_service()

# Generate unique id and api_key
generated_id = generate_unique_id()
generated_apikey = generate_api_key()

@app.get("/")
def read_root():
    return {"message": "Order Service for Saqib's online mart"}

@app.post("/orders", response_model=Order)
async def create_order(
    payload: OrderCreated,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    client: Union[MockOrderService, Client] = Depends(get_client),
    session: Session = Depends(get_session)
    ): 
    if isinstance(client, MockOrderService):
        model = MockOrder
    else:
        model = Order
    try:
        order_info = {
            "id": generated_id,
            "item_name": payload.item_name,
            "quantity": payload.quantity,
            "price": payload.price,
            "status": "pending",
            "user_email": payload.user_email,
            "user_phone": payload.user_phone,
            "api_key": generated_apikey,
            "source": "mock" if isinstance(client, MockOrderService) else "real"
        }

        # Execute order creation and receive response
        response = client.auth.create_order(order_info)

        # Check if response is a dictionary and properly formatted
        if response and isinstance(response, dict):
            created_order= Order(**response)

            # Save order to the database
            if response and isinstance(response, dict):
                new_order = model(
                    id=created_order.id,
                    item_name=created_order.item_name,
                    quantity=created_order.quantity,
                    price=created_order.price,
                    status=created_order.status,
                    user_email=created_order.user_email,
                    user_phone=created_order.user_phone,
                    source=created_order.source,
                    api_key=created_order.api_key
                )
            session.add(new_order)
            session.commit()
            
            logging.info(f'ORDER_SAVED_SUCCESSFULLY_IN_DB : {new_order}')
        else:  
            raise HTTPException(status_code=500, detail="FAILED_TO_CREATE_ORDER")

        await send_order_status_notification(new_order, producer)
        logging.info(f'NEW_ORDER_CREATED_AND_SAVED: {new_order}')
    
    except Exception as e:  
        logging.error(f'ERROR****:{str(e)}')  
        raise HTTPException(status_code=500, detail=str(e))  # Return an error message  
                
    return new_order
    
    
@app.put("/orders/{order_id}")
async def update_order(
    order_id: str,
    payload: OrderCreated,
    api_key: str = Header(..., alias="apikey"),
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    client: Union[MockOrderService, Client] = Depends(get_client),
    session: Session = Depends(get_session)
    ):
    if isinstance(client, MockOrderService):
        model= MockOrder
    else:
        model= Order
    try:
        user= validate_api_key(api_key)
        fetched_api_key = user.get('api_key')  # Fetch API key from user_info
        
        order_info = {
            "id": order_id,
            "item_name": payload.item_name,
            "quantity": payload.quantity,
            "price": payload.price,
            "status": "pending",
            "user_email": payload.user_email,
            "user_phone": payload.user_phone,
            "api_key": fetched_api_key,
            "source": "mock" if isinstance(client, MockOrderService) else "real"
        }    
        response = client.auth.update_order(order_id, order_info)
        if response and isinstance(response, dict):
            # Use unpacking if response matches Order fields
            updated_order = Order(**response)
            # Save order to the database
            new_updated_order = model(**updated_order.dict())

            session.merge(new_updated_order)
            session.commit()
            logging.info(
                f'\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n'
                f'\nORDER_UPDATED__SAVED__AND_SEND_TO_NOTIFCATION_SERVICE\n:'
                f'\n{new_updated_order}\n'
                f'\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n'
                )
            
            await send_order_status_notification(new_updated_order, producer)
            return new_updated_order

        raise HTTPException(status_code=404, detail="Order not found")

    except Exception as e:
        session.rollback()
        logging.error(f'Error updating order: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/orders/{order_id}')
def track_order(
    order_id: str,
    client: Union[MockOrderService, Client]= Depends(get_client)
    ):
    
    tracked_order= client.auth.track_order(order_id)
    logging.info(
                f'\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n'
                f'\nTRACKED_ORDER\n:'
                f'\n{tracked_order}\n'
                f'\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n'
                )
    return {f'TRACKED_RECORD : {tracked_order}\n'}

@app.delete("/orders/{order_id}")
async def delete_order(
    order_id: str,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    client: Union[MockOrderService, Client] = Depends(get_client),
    session: Session= Depends(get_session)
):
    if isinstance(client, MockOrderService):
        model= MockOrder
    else:
        model= Order
    
    response= client.auth.delete_order(order_id)
    
    if response and isinstance(response, dict):
    # Create a model instance from the response
        order_instance = model(**response)
        
        # Fetch the existing order from the session using the order ID
        existing_instance = session.get(model, order_instance.id)
        if existing_instance:
            session.delete(existing_instance)
            session.commit()
            
            logging.info(
                f'\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n'
                f'\nMENTIONED_ORDER_DELETED_SUCCESSFULLY\n:'
                f'\n{existing_instance}\n'
                f'\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n'
            )
            return {
                f'DELETED_RECORD : {existing_instance}'
            }
        else:
            raise HTTPException(status_code=404, detail="RECORD_NOT_FOUND")

@app.get("/orders", response_model=List[Order])
async def get_orders_list(
    producer: AIOKafkaProducer=Depends(get_kafka_producer),
    client: Union[MockOrderService, Client] = Depends(get_client)):
    
    orders_list = client.auth.get_orders_list()
    # Convert the orders list to a JSON string with pretty formatting
    formatted_json = json.dumps(orders_list, indent=4)
    
    logging.info(f'{formatted_json}')
    # Return the formatted JSON as a response with appropriate headers
    await send_order_status_notification(orders_list, producer)
    return Response(content=formatted_json, media_type="application/json")
    
