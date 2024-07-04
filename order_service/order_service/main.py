import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from .dependencies import get_mock_order_service, get_real_order_service
from .model import Order
from .mock_order_service import MockOrderService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# In-memory storage for orders
orders_db = []
order_id_counter = 1

mock_supabse=os.getenv('MOCK_SUPABASE', 'True').lower() == 'true'
def get_order(): # dpendency injection
    if mock_supabse:
        return get_mock_order_service()
    return get_real_order_service() 

@app.get("/")
def read_root():
    return {"message": "Order Service"}

@app.post("/create_order", response_model=Order)
async def create_order(order:Order, service:MockOrderService=Depends(get_order)):
    order_data= order.model_dump()
    created_order= service.create_order(order_data)
    logging.info(f'Created_Order : {created_order}')
    return created_order

@app.put("/update_order/{order_id}", response_model=Order)
async def update_order(order_id:int, order:Order, service: MockOrderService=Depends(get_order)):
    update_data= order.model_dump() #from json_string to python_dict
    updated_order= service.update_order(order_id, update_data)
    logging.info(f'updated_Order : {updated_order}')
    if updated_order:
        return updated_order
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.get("/track_order/{order_id}", response_model=Order)
async def track_order(order_id:int, service: MockOrderService=Depends(get_order)):
    tracked_order= service.track_order(order_id)
    logging.info(f'Tracked_order : {tracked_order}')
    if tracked_order:
        return tracked_order
    raise HTTPException(status_code=404, detail="Order not found")

@app.delete("/delete_order/{order_id}", response_model=Order)
async def delete_order(order_id:int, service: MockOrderService=Depends(get_order)):
    deleted_order= service.delete_order(order_id)
    logging.info(f'Deleted_order : {deleted_order}')
    if deleted_order:
        return deleted_order
    raise HTTPException(status_code=404, detail="Order not found")


@app.get("/orders_list", response_model=List[Order])
async def get_orders_list(service: MockOrderService=Depends(get_order)):
    return service.orders_list()

