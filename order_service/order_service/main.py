from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List
from aiokafka import AIOKafkaProducer
from .notification import send_order_status_notification, send_user_info_notification
from .producer import get_kafka_producer
from .dependencies import get_mock_order_service, get_real_order_service
from .model import Order, NotificationPayload, OrderCreated
from .settings import settings
import logging, asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='SaqibShopSphere _ Order Service',
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
        status=created_order.status
    )
    await send_order_status_notification(order_status_payload, producer)

    # Prepare user information for notification
    # user_info_payload = NotificationPayload(
    #     order_id=created_order.id,
    #     status="created",
    #     user_email="user@example.com",  # You would get this from the actual user data
    #     user_phone="+1234567890"         # You would get this from the actual user data
    # )
    # await send_user_info_notification(user_info_payload, producer)

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
        status=updated_order.status
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
        status=response.status
    )
        await send_order_status_notification(order_status_payload, producer)

        logging.info(f'ORDER_DELETED : {response}')
        return {"message": "ORDER_DELETED_SUCCESSFULLY"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.get("/orders", response_model=List[Order])
async def get_orders_list(service = Depends(get_order_service)):
    order_list = service.orders_list()
    logging.info(f'ORDER_LIST : {order_list}')
    return service.orders_list()
