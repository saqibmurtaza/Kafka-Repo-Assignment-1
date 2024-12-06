from fastapi import HTTPException, Depends
from supabase import Client
from urllib.parse import unquote
from .database import supabase
from .models import Order, MockOrder
from .mock_order import MockOrderService
import requests, logging, json, logging

# FETCHED DATA THROUGH API CALLS

def fetch_product(product_name:str):
    
    decoded_product_name = unquote(product_name).strip()
    logging.info(f"Decoded and Trimmed poduct_Name: {decoded_product_name}")

    response= requests.get(f"http://product_02:8007/api/product/{product_name}")
    response.raise_for_status() 
    try:
        product= response.json()
        return product
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch product data FROM_PRODUCT_SERVICE")
    
def fetch_inventory(name:str, apikey:str, token:str):

    decoded_inv_name = unquote(name).strip()
    logging.info(f"Decoded and Trimmed inventory_Name: {decoded_inv_name}")

    headers={
        "apikey": apikey,
        "token": token
    }

    inventory_url= f"http://inventory_service:8011/api/inventory/{decoded_inv_name}"
    response= requests.get(inventory_url, headers=headers)
    response.raise_for_status()

    try:
        inventory= response.json()
        if not inventory:
            logging.info(f"ITEM_NOT_FOUND_IN_STOCK")
        logging.info(f"STOCK_IN_HAND_FROM_INVENTORY_SERVICE: {inventory}")
        return inventory

    except ValueError:
        logging.error("Failed to parse inventory response as JSON")
        raise

# Fetch Data from Database

async def fetch_cart_data(client):

    model= MockOrder if isinstance(client, MockOrderService) else Order
    table_name= 'mockorder' if model is MockOrder else 'order'

    # Fetch Data from Supabase
    response= supabase.table(table_name).select('*').execute()
    fetch_data= response.json()
    if isinstance(fetch_data, str):
        fetch_data= json.loads(fetch_data)
    
    data= fetch_data.get('data', [])
    return data

def fetch_data(id:int):
    response= supabase.from_('catalogue').select('*').eq('id', id).execute()
    
    response_dict= response.json()
    if isinstance(response_dict, str):
        response_dict= json.loads(response_dict)

    for my_data in response_dict.get('data', []):
        if my_data['id'] == id:
            fetched_product= my_data
        return fetched_product
    None



# def update_order_status(payload: dict):

#     url = "http://order_service:8010/api/orders/order_status"
    
#     try:
#         # Send the POST request with the payload as JSON data
#         response = requests.post(url, json=payload)
#         response.raise_for_status()  # Check for HTTP errors
        
#         # Return the JSON response if successful
#         return response.json()
    
#     except requests.exceptions.RequestException as e:
#         # Raise an HTTPException if the request fails
#         raise HTTPException(status_code=500, detail="Failed to update order status")

# FETCHED VIA DATABASE

# EXTRACT DATA FROM DB TABLE CATALOGUE OF PRODUCT SERVICE 

