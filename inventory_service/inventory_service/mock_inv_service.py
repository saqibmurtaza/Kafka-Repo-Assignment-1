from fastapi import HTTPException
from .settings import settings
from .model import Inventory, User
import logging, jwt, requests

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)


class MockInventoryService:
    def __init__(self):
        self.inventory = []
        self.users = []
        self.access_token = None

    # def get_user_profile(self, user_id: int):
    #     logger.info(f'Calling get_user_profile with user_id: {user_id}')
    #     # Make an HTTP request to the user service to fetch the user profile
    #     response = requests.get(f'http://localhost:8009/user/profile/{user_id}')
    #     logger.info(f'Response from user service: {response.status_code}, {response.text}')

    #     if response.status_code == 200:
    #         return response.json()
    #     return None
    
    def get_user_profile(self, user_id: int):
        url = f'http://user_service:8009/user/profile/{user_id}'
        logger.info(f'Sending GET request to URL: {url}')
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses
            logger.info(f'Response status code: {response.status_code}')
            logger.info(f'Response content: {response.content}')
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err}')
        except Exception as err:
            logger.error(f'Other error occurred: {err}')
        return None

    def get_user_by_id(self, user_id: int):  # <--- Added method to get user by ID
        for user in self.users:
            if user["id"] == user_id:
                return user
        return None

    
    def verify_token(self, acees_token: str):
        try:
            payload = jwt.decode(acees_token, settings.JWT_SECRET, 
                                 algorithms=[settings.JWT_ALGORITHM])  # <----
            logger.info(f'Decoded payload: {payload}')
            user_id = payload["user_id"]
            # Assuming you have a method to get user profile by user_id
            user_profile = self.get_user_profile(user_id)
            logging.info(f'User profile fetched: {user_profile}')
            return user_profile
        except jwt.ExpiredSignatureError:
            logger.error('Token has expired')
            return None
        except jwt.DecodeError:
            logger.error('Invalid token')
            return None 
    
    def create_inventory(self, item_data:Inventory):
        item_data["id"]= len(self.inventory) + 1
        item_data["stock_value"] = item_data["stock_in_hand"] * item_data["unit_price"]
        self.inventory.append(item_data)
        logger.info(f'Created Inventory Item: {item_data}')  # <--- Added logging
        return item_data
    
    def track_inventory(self, item_id:int, access_token):
        payload= self.verify_token(access_token)
        logging.info(f'PROFILE_FETCHED_IN_INV_SERVICE : {payload}')
        for my_item in self.inventory:
            if my_item["id"] == item_id:
                return {
                "item_name": my_item["item_name"],
                "quantity": my_item["quantity"],
                "threshold": my_item["threshold"],
                "email": my_item["email"],
                "status": "success"
            }
        return None
    
    def update_inventory(self, item_id:int, update_data:Inventory, token: str):

        user_profile = self.verify_token(token)  # Verify token and fetch user profile <----
        if user_profile is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")  # <----

        for my_item in self.inventory:
            if my_item["id"] == item_id:
                update_data["stock_value"] = update_data["stock_in_hand"] * update_data["unit_price"]
                my_item.update(update_data)
                logger.info(f'Updated Inventory Item: {my_item}')  # <--- Added logging
                return my_item
        return None
    
    def delete_inventory(self, item_id:int):
        for my_item in self.inventory:
            if my_item["id"] == item_id:
                self.inventory.remove(my_item)
                logger.info(f'Deleted Inventory Item: {my_item}')  # <--- Added logging
                return my_item
        return None
    
    def stock_list(self):
        return self.inventory
