from fastapi import FastAPI, Depends, HTTPException, Request
from sqlmodel import Session
from contextlib import asynccontextmanager
from typing import List, Union
from supabase import Client
from aiokafka import AIOKafkaProducer
from .notify_logic import send_order_status_notification, send_batch_notifications
from .producer import get_kafka_producer
from .database import create_db_tables, get_session, supabase
from .dependencies import get_mock_order_service, get_real_order_service
from .models import OrderCreate, OrderUpdate, OrderStatusUpdate, MockOrderService, Cart, MockCart
from .settings import settings
from .fetch_functions import fetch_inventory, fetch_data, fetch_cart_data
from .payment_logic.pay_process import process_payment
from .order_pb2 import OrderProto, NotifyOrder
from .auth_handler import AuthMiddleware
import logging, asyncio, json, requests, traceback, uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('CREATING_TABLES...................................')
    try:
        create_db_tables()
        logging.info(f'\nTABLES_CREATED_SUCCESSFULLY\n')
    except Exception as e:
        logging.error(f'\nAN_ERROR_OCCURED_IN_BLOCK_CONTEXT_MANAGER : {str(e)}...............\n')
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
"""
Extract API key, token, and email from request context, if you need because
it holds in request context
    api_key = request.state.apikey
    token = request.state.token
    email = request.state.email

"""
# Add the authentication middleware globally
app.add_middleware(AuthMiddleware)

def get_client() -> Union[MockOrderService, Client]:
    if settings.MOCK_SUPABASE:
        return get_mock_order_service()
    return get_real_order_service()

@app.get("/")
def read_root():
    return {"message": "Order Service for Saqib's online mart"}

@app.post("/cart", response_model=Cart)
async def add_to_cart(
    payload: OrderCreate,
    request: Request,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    client: Union[MockOrderService, Client] = Depends(get_client),
    session: Session = Depends(get_session)
    ): 
    
    model= MockCart if isinstance(client, MockOrderService) else Cart
    
    try:
        catalogue_items= fetch_data(payload.id)
        if not catalogue_items:
            raise HTTPException(status_code=404, detail=f"ITEM_NOT_FOUND_IN_CATALOGUE_OF_ID_{payload.id}")


        product_name= catalogue_items['product_name']
        item_description= catalogue_items['description']
        product_price= catalogue_items['price']

        logging.info(
            f"product_name : {product_name}\n"
            f"description : {item_description}\n"
            f"product_price : {product_price}\n"
        )

        """
        EXTRACT QUANTITY FROM INVENTORY_SERVICE
        pass apikey & token, inventory_service authorized it & respond.
        We therfore, store infos in request_context of BaseHTTPMiddleware,
        for golbally used these infos, required
        """
        ##########################
        inventory_details= fetch_inventory(
            product_name,
            apikey= request.state.apikey,
            token= request.state.token
            )
        
        if not inventory_details:
            raise HTTPException(status_code=404, detail='ITEM_IS_OUT_OF_STOCK')

        for my_inv in inventory_details:
            stock_in_hand= my_inv['stock_in_hand']

        #Generate order_id
        def generate_unique_id():
            return str(uuid.uuid4())
        
        generated_id= generate_unique_id()

        create_order= OrderProto(
            id= generated_id,
            item_name= product_name,
            description= item_description,
            quantity= payload.quantity,
            price= product_price,
            payment_status= 'Pending',
            user_email= payload.user_email
        )
    
        # CHECK QUANTITY
        if create_order.quantity > stock_in_hand:
            raise HTTPException(status_code=400, detail=
                    f"ENTERED_QTY {create_order.quantity}_EXCEEDS__"
                    f"THE_AVAILABLE_STOCK_QTY_{stock_in_hand}__"
                    f"FOR_THE_PRODUCT_{create_order.item_name}"
                    )
        
        order_dict= {
            "id": generated_id,
            "item_name": product_name,
            "description": item_description,
            "quantity": payload.quantity,
            "price": product_price,
            "payment_status": "Pending",
            "user_email": payload.user_email
        }
        # Create Instance of model
        
        order = model(**order_dict)

        session.add(order)
        session.commit()
        logging.info(f"NEW_ORDER_CREATED_AND_SAVED_TO_DB")

        # Prepare Message for sending via Kafka - Serialize to protobuf bytes
        order_instance= NotifyOrder(action='create', data=create_order)
        order_bytes= order_instance.SerializeToString()
        
        # SENT NOTIFICATIONS
        await send_order_status_notification(order_bytes, producer=producer)
            
        logging.info(
            f'\n!****!****!****!****!****!****!****!****!****!****!****!****!\n'
            f'NEW_ORDER_SENT_TO_NOTIFICATION_SERVICE_VIA-KAFKA:\n'
            f'{create_order}'
            f'\n!****!****!****!****!****!****!****!****!****!****!****!****!\n')

        return order
    # INFORM THE EXACT LOCATION AND DETAILS ABOUT ERRORS    
    except Exception as e:
        error_details = traceback.format_exc()  # Get the complete traceback
        logging.error(f"Error occurred: {str(e)}\nTraceback:\n{error_details}")
        raise HTTPException(status_code=500, detail=str(e))
        
@app.put("/cart/{order_id}")
async def update_cart(
    order_id: str,
    payload: OrderUpdate,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    client: Union[MockOrderService, Client] = Depends(get_client),
    session: Session = Depends(get_session)
):
    # Dynamically choose model based on client type
    model = MockCart if isinstance(client, MockOrderService) else Cart

    try:
        # Check if order exists in the database before updating
        response = supabase.from_('mockorder').select('*').eq('id', order_id).execute()
        if not response:
            raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")

        """
        Note: Extracted data from DB is of type list stored in variable 'data'
        Convert Extracted data from db
        1: convert it to json_formatted string
        2: To dict
        3. Iterate over the list & update keys, values
        """
        response_str= response.json()
        response_dict= json.loads(response_str)

        order= response_dict.get('data', [])
        
        payload_dict= payload.dict()

        for my_order in order:
            for key, value in payload_dict.items():
                if key in my_order: # it checks whether the key from the payload dictionary exists as a key in the my_order dictionary
                    my_order[key] = value # This updates the value of an existing key in the my_order dictionary with the CORRESPONDING value from the payload dictionary
            updated_order= my_order
            
            # Unpack Dict & create instance to save in db
            order_instance= model(**updated_order)
            
            # Save to DB
            session.merge(order_instance)
            session.commit()

            """
            Prepare message for sending to Notification Service
            1: call function and pass action and OrderProto_instance(Proto)
            """
             # Convert the SQLModel instance to a Protobuf message
            order_proto = OrderProto(
                id=order_instance.id,
                item_name=order_instance.item_name,
                description=order_instance.description,
                quantity=order_instance.quantity,
                price=order_instance.price,
                payment_status=order_instance.payment_status,
                user_email=order_instance.user_email
            )
            
            message= NotifyOrder(action='update', data=order_proto)
            order_in_bytes= message.SerializeToString()

            await send_order_status_notification(order_in_bytes, producer=producer)
            
            logging.info(
                f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
                f"ORDER_UPDATED__SAVED__AND_SENT_TO_NOTIFICATION_SERVICE\n"
                f"{order_instance}\n"
                f"!\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
            )
            
            # Return the updated order
            return order_instance

    except Exception as e:
        error_details = traceback.format_exc()  # Get the complete traceback
        logging.error(f"Error occurred: {str(e)}\nTraceback:\n{error_details}")
        raise HTTPException(status_code=500, detail=str(e))
        

@app.get('/cart/{order_id}')
def track_cart_item(
    order_id: str,
    client: Union[MockOrderService, Client]= Depends(get_client)
    ):

    model= MockCart if isinstance(client, MockOrderService) else Cart
    table_name = 'mockcart' if model is MockCart else 'cart'


    try:
        response = supabase.table(table_name).select('*').eq('id', order_id).execute()
        logging.info(f"RESPONSE:{response}")

        fetched_order = response.json()

        if isinstance(fetched_order, str):
            fetched_order = json.loads(fetched_order)

        # Iterate over the orders found in the 'data' field
        for my_order in fetched_order.get('data', []):
            if my_order.get('id') == order_id:
                tracked_order= my_order

        logging.info(
                    f'\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n'
                    f'\nTRACKED_ORDER:\n'
                    f'\n{tracked_order}\n'
                    f'\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n'
                    )
        return {f'TRACKED_RECORD : {tracked_order}'}
    except Exception as e:
        error_details = traceback.format_exc()
        logging.error(f"ERROR_TRACEBACKE: {error_details}\nERROR_STATUS:{str(e)}")
        raise HTTPException(status_code=500, detail=f"ERROR STATUS {str(e)}")

@app.delete("/cart/{order_id}")
async def delete_cart_item(
    order_id: str,
    producer: AIOKafkaProducer= Depends(get_kafka_producer),
    client: Union[MockOrderService, Client] = Depends(get_client),
):
    model= MockCart if isinstance(client, MockOrderService) else Cart
    table_name = 'mockcart' if model is MockCart else 'cart'

    # Fetch the record from Supabase
    response = supabase.table(table_name).select('*').eq('id', order_id).execute()
    fetched_data = response.json()

    if isinstance(fetched_data, str):
        fetched_data = json.loads(fetched_data)

    data = fetched_data.get('data', [])
    logging.info(f"data******************** {data}")
    
    if not data:
        logging.warning(
            f"Order with ID {order_id} not found in table '{table_name}'. Supabase response: {fetched_data}"
        )
        return {"error": f"Order with ID {order_id} not found in {table_name}."}

    # Delete the record from Supabase
    delete_response = supabase.table(table_name).delete().eq('id', order_id).execute()
    delete_result = delete_response.json()

    # Log deletion
    logging.info(
        f"\n!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
        f"Mentioned order deleted successfully from Supabase:\n{delete_result}\n"
        f"!****!****!****!****!****!****!****!****!****!****!****!****!****!****!****!\n"
    )
    """ 
    PREPARE MESSAGE TO SEND VIA KAFKA
    1: Create the NotifyOrder message 
    (create OrderProto Instance for passing to NotifyOrder)
    2: serialize message to protobuf bytes for sending via Kafka
    """
    for my_data in data:
        logging.info(f"MY DATA :{my_data}")

    # Create the NotifyOrder message
    order_proto = OrderProto(
        id=my_data["id"],
        item_name=my_data["item_name"],
        description=my_data.get("description", ""),
        quantity=my_data["quantity"],
        price=my_data["price"],
        payment_status=my_data.get("payment_status", "unknown"),
        user_email=my_data.get("user_email", ""),
    )

    message = NotifyOrder(
        action="delete",
        data=order_proto,
    )
    # Serialize the message to a dictionary for logging or sending to Kafka
    serialized_msg= message.SerializeToString()
    await send_order_status_notification(serialized_msg, producer)

    return delete_result

@app.get("/cart", response_model=List[Cart])
async def view_cart_items(
    producer: AIOKafkaProducer=Depends(get_kafka_producer),
    client: Union[MockOrderService, Client] = Depends(get_client)):
    
    model= MockCart if isinstance(client, MockOrderService) else Cart
    table_name = 'mockcart' if model is MockCart else 'cart'

    # Fetch Data from Supabase
    response= supabase.table(table_name).select('*').execute()
    fetch_data= response.json()
    if isinstance(fetch_data, str):
        fetch_data= json.loads(fetch_data)
    
    # Convert the orders list to a JSON string with pretty formatting
    formatted_json = json.dumps(fetch_data, indent=4)
    logging.info(f'{formatted_json}')

    orders= fetch_data.get('data', [])
    
    # Create a list of NotifyOrder messages
    notify_orders = []

    for my_order in orders:
        # Map database fields to OrderProto
        order_proto = OrderProto(
            id=my_order["id"],
            item_name=my_order["item_name"],
            description=my_order.get("description", ""),
            quantity=my_order["quantity"],
            price=my_order["price"],
            payment_status=my_order.get("payment_status", "unknown"),
            user_email=my_order.get("user_email", ""),
        )

        # Create NotifyOrder message
        message = NotifyOrder(
            action="view",  # Action could be "view" or "list" for this endpoint
            data=order_proto,
        )
        notify_orders.append(message)

    # Send all messages in a single batch
    await send_batch_notifications(notify_orders, producer)

    # Return the orders as JSON
    return orders

# CART FUNCTIONALITY
# @app.post("/cart", response_model=MockCart)
# async def add_to_cart(
#     payload: CartPayload,
#     request: Request,
#     client: Union[Client, MockOrderService] = Depends(get_client),
#     session: Session = Depends(get_session)
# ):

#     cart_service = CartService(session, client, request)
#     return await cart_service.add_to_cart(payload)

# @app.put("/cart/{cart_id}")
# async def update_cart(
#     cart_id: str,
#     payload: CartPayload,
#     client: Union[Client, MockOrderService] = Depends(get_client),
#     session: Session = Depends(get_session)
# ):
    
#     cart_service = CartService(session, client)
#     return await cart_service.update_cart(cart_id, payload)

# @app.delete("/cart/{cart_id}")
# async def delete_cart_item(
#     cart_id: str,
#     client: Union[Client, MockOrderService] = Depends(get_client),
#     session: Session = Depends(get_session)
# ):
#     cart_service = CartService(session, client)
#     return await cart_service.delete_cart_item(cart_id)

# @app.get("/cart")
# async def view_cart(
#     client: Union[Client, MockOrderService] = Depends(get_client),
#     session: Session = Depends(get_session)
# ):
#     cart_service = CartService(session, client)
#     return await cart_service.view_cart()

@app.post("/cart/checkout")
async def checkout(
    request: Request,
    client: Union[Client, MockOrderService] = Depends(get_client),
):
    apikey= request.state.apikey
    token= request.state.token

    cart_data_fetched= await fetch_cart_data(client)

    total_price= 0 # initialize local variable
    for my_item in cart_data_fetched:
        total_price += my_item['price'] * my_item['quantity']

    logging.info(f"\n**********\nTOTAL_PRICE:{total_price}\n**********")
    
    # Create a payload for payment processing
    payment_payload = OrderProto(id="cart-checkout", price=total_price)

    # Process the payment
    payment_status = await process_payment(payment_payload)

    # Deduct items from inventory
    if payment_status == 'CONFIRMED':
        for my_item in cart_data_fetched:
            item_name= my_item['item_name']
            quantity= my_item['quantity']

            # Fetch the item from the inventory service
            inventory_items= fetch_inventory(item_name, apikey, token)

            for my_inv in inventory_items:
                if my_inv and my_inv['stock_in_hand'] >= quantity:
                    new_stock= my_inv['stock_in_hand'] - quantity
                
                    # Update the inventory via an API call
                    update_response = requests.put(
                            f"http://inventory_service:8011/api/inventory/{item_name}",
                            json={"stock_in_hand": new_stock},
                            headers={
                                "token": token,
                                "apikey": apikey
                            }
                        )
                    update_response.raise_for_status()  # Raise exception if update fails
                    logging.info(f"Updated stock for item {item_name}: {new_stock}")
                else:
                    # Handle cases where the item is out of stock or insufficient
                    logging.warning(f"{item_name}_OUT_OF_STOCK")
                    return {"error": "ITEM_OUT_OF_STOCK"}

        # Return the payment status
        return {
            "TOTAL_PRICE": total_price, 
            "PAYMENT_STATUS": payment_status,
            "MESSAGE": f"Updated stock for item {item_name}: {new_stock}"
            }

@app.post("/api/orders/order_status")
async def update_order_status(
    payload: OrderStatusUpdate,
    client: Union[MockOrderService, Client] = Depends(get_client),
    session: Session = Depends(get_session)):

    if isinstance(client, MockOrderService):
        model = MockCart
    else:
        model = Cart
    try:
        # Fetch the order from the database using the provided order_id
        order = session.query(model).filter(model.id == payload.order_id).first()

        # Check if order exists
        if not order:
            logger.error(f"Order {payload.order_id} not found.")
            raise HTTPException(status_code=404, detail=f"Order {payload.order_id} not found.")

        # Update the order's status
        order.status = payload.status
        session.add(order)
        session.commit()

        logger.info(f"Order {payload.order_id} updated to {payload.status}")
        return {"message": f"Order {payload.order_id} updated to {payload.status}"}

    except Exception as e:
        logger.error(f"Failed to payload order {payload.order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to payload order status")


"""
NOTE:Refresh Requirement: The .refresh() method only works on 
entities that were added to or loaded by the session directly. 
Without prior attachment (via add or merge), refresh cannot reload 
the data.
"""

