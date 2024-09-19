from fastapi import HTTPException
from order_service.order_pb2 import OrderProto
from .database import supabase
from .models import MockTable
import logging, secrets, uuid, json

def generate_api_key():
    return secrets.token_hex(16)

def generate_unique_id():
    return str(uuid.uuid4())

class MockOrderService:
    def __init__(self):
        self.orders = []
        self.auth= MockOrderAuth(self.orders)
    
    def table(self, name:str):
        if name == 'mock_order':
            return MockTable(self.orders)
        raise ValueError(f"NO_MOCK_TABLE_FOR_NAME {name}")
    
class MockOrderAuth():
    def __init__(self, order):
        self.orders= order 

    def create_order(self, order_data):

        existing_order_response = supabase.from_('mockorder').select().eq('id', order_data['id']).execute()
    
        # Convert to string
        existing_order_str = existing_order_response.json()
        # Convert string to dictionary
        existing_order_dict= json.loads(existing_order_str) 

        # If an existing order is found, raise an exception  
        if existing_order_dict.get('data'):  
            raise HTTPException(status_code=409, details='ORDER_ID_EXIST')  
        
        # Create a new order and add it to the list
        order_proto = OrderProto(
            id=order_data['id'],
            item_name=order_data['item_name'],
            quantity=order_data['quantity'],
            price=order_data['price'],
            status=order_data['status'],
            user_email=order_data['user_email'],
            user_phone=order_data['user_phone'],
            source=order_data['source'],
            api_key=order_data['api_key']
        )
        self.orders.append(order_proto)
    
        order_data_response = {  
            "id": order_proto.id,  
            "item_name": order_proto.item_name,  
            "quantity": order_proto.quantity,  
            "price": order_proto.price,  
            "status": order_proto.status,  
            "user_email": order_proto.user_email,  
            "user_phone": order_proto.user_phone,  
            "source": order_proto.source,  
            "api_key": order_proto.api_key  
        }  

        return order_data_response
    
    def update_order(self, order_id: str, payload):
        response = supabase.from_('mockorder').select('*').eq('id', payload['id']).execute()

        # Ensure this returns a dictionary
        existing_order_dict = response.json()
        if isinstance(existing_order_dict, str):
            # Use json.loads only if it's a string
            existing_order_dict = json.loads(existing_order_dict)

        for my_order in existing_order_dict.get('data', []):  # Use .get('data', []) to safely access the list of orders
            if my_order.get('id') == order_id:
                for key, value in payload.items():
                    if key in my_order:
                        my_order[key] = value
                        updated_order = my_order
                return updated_order
        return None
    
    def track_order(self, order_id: str):
        response = supabase.table('mockorder').select('*').eq('id', order_id).execute()

        existing_order = response.json()

        if isinstance(existing_order, str):
            existing_order = json.loads(existing_order)

        # Iterate over the orders found in the 'data' field
        for my_order in existing_order.get('data', []):
            if my_order.get('id') == order_id:
                logging.info(f'MY_ORDER: {my_order}')
            return my_order
        return None  # Return None if no order is found

    def delete_order(self, order_id: int):
        response = supabase.table('mockorder').select('*').eq('id', order_id).execute()
        response_json = response.json()

        if isinstance(response_json, str):
            response_json = json.loads(response_json)

        for my_order in response_json.get('data', []):
            if my_order.get('id') == order_id:
                return my_order
        return None


    def get_orders_list(self):
        response= supabase.table('mockorder').select('*').execute()
        orders_list= response.data
        return orders_list
    
    
