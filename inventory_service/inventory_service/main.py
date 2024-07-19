from fastapi import FastAPI, Depends, HTTPException
from .model import Inventory, InventoryResponse
from .dependencies import get_mock_inventory, get_real_inventory
from .mock_inv_service import MockInventoryService
import logging, os

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

app = FastAPI(
    title= 'ShopSphere _ Inventory Service',
    servers=[
        {
        "url": "http://localhost:8005",
        "description": "Server:Uvicorn, port:8005"
        }]
    )

mock_supabase= os.getenv("MOCK_SUPABSE", 'true').lower() == 'true'

def get_inventory(): #dependency_injection function
    if mock_supabase:
        return get_mock_inventory()
    return get_real_inventory()

@app.get("/")
async def read_root():
    return {"message" : "Inventory Service"}

@app.post("/create_inventory", response_model=InventoryResponse)
async def create_inventory(inventory:Inventory, service: MockInventoryService=Depends(get_inventory)):
    response= inventory.model_dump()
    created_inventory= service.create_inventory(response)
    logging.info(f'Inventory_Item : {created_inventory}')    
    return created_inventory

@app.get("/track_inventory/{item_id}", response_model=InventoryResponse)
async def track_inventory(item_id:int, service: MockInventoryService=Depends(get_inventory)):
    tracked_inventory= service.track_inventory(item_id)
    logging.info(f'Tracked_inventory_item : {tracked_inventory}')
    if tracked_inventory:
        return tracked_inventory
    raise HTTPException(status_code=404, detail='Item not found in Inventory')

@app.put("/update_inventory/{item_id}", response_model=InventoryResponse)
async def update_inventory(item_id:int, update_data:Inventory, service: MockInventoryService=Depends(get_inventory)):
    response= update_data.model_dump()
    updated_stock= service.update_inventory(item_id, response)
    logging.info(f'Updated_stock : {updated_stock}')
    if updated_stock:
        return updated_stock
    raise HTTPException(status_code=404, detail='Item not found in Inventory')

@app.delete("/delete_inventory/{item_id}", response_model=InventoryResponse)
async def delete_inventory(item_id:int, service: MockInventoryService=Depends(get_inventory)):
    deleted_stock= service.delete_inventory(item_id)
    logging.info(f'Deleted_Stock : {deleted_stock}')
    if deleted_stock:
        return deleted_stock
    raise HTTPException(status_code=404, detail='item not found')

@app.get("/stock_list", response_model=list[InventoryResponse])
async def get_stock_list(service: MockInventoryService=Depends(get_inventory)):
    inventory_list= service.stock_list()
    logging.info(f'Stock_List : {inventory_list}')
    return inventory_list