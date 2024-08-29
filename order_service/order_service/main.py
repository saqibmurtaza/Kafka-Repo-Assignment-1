from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from typing import List
from aiokafka import AIOKafkaProducer
from .notification import send_order_status_notification
from .producer import get_kafka_producer
from .dependencies import get_mock_order_service, get_real_order_service
from .model import Order, OrderCreated
from .settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
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

def get_order_service():
    if settings.MOCK_SUPABASE:
        return get_mock_order_service()
    return get_real_order_service()

@app.get("/")
def read_root():
    return {"message": "Order Service for Saqib's online mart"}

@app.post("/orders", response_model=Order)
async def create_order(
    order: OrderCreated,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    service = Depends(get_order_service)
):
    order_data = order.model_dump()  # Convert the order instance into a dictionary
    created_order = service.create_order(order_data)
    logging.info(f'ORDER_CREATED : {created_order}')

    order_status_payload = OrderCreated(
        item_name=created_order.item_name,
        quantity=created_order.quantity,
        price=created_order.price,
        status=created_order.status,
        user_email=created_order.user_email,
        user_phone=created_order.user_phone
    )
    await send_order_status_notification(order_status_payload, producer)

    return created_order

@app.put("/orders/{order_id}", response_model=Order)
async def update_order(
    order_id: int,
    order: OrderCreated,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    service = Depends(get_order_service)
):
    update_data = {k: v for k, v in order.model_dump().items() if k != 'id'}
    updated_order = service.update_order(order_id, update_data)
    logging.info(f'ORDER_UPDATED : {updated_order}')

    if updated_order:
        order_status_payload = OrderCreated(
        item_name=updated_order.item_name,
        quantity=updated_order.quantity,
        price=updated_order.price,
        status=updated_order.status,
        user_email=updated_order.user_email,
        user_phone=updated_order.user_phone
    )
        await send_order_status_notification(order_status_payload, producer)
        return updated_order
    else:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")

@app.delete("/orders/{order_id}", response_model=dict)
async def delete_order(
    order_id: int,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    service = Depends(get_order_service)
):
    response = service.delete_order(order_id)
    if response:
        order_status_payload = OrderCreated(
        item_name=response.item_name,
        quantity=response.quantity,
        price=response.price,
        status=response.status,
        user_email=response.user_email,
        user_phone=response.user_phone
    )

        logging.info(f'ORDER_DELETED : {response}')
        return {"message": "ORDER_DELETED_SUCCESSFULLY"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.get("/orders", response_model=List[Order])
async def get_orders_list(service = Depends(get_order_service)):
    order_list = service.orders_list()
    logging.info(f'ORDER_LIST : {order_list}')
    return service.orders_list()
