from .inventory_pb2 import InventoryUpdates as InvMessage
from .models import Inventory
from .email_function import send_email
import json, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#################################################
##### INVENTORY_SERVICE_MESSAGE_PROCEESSING_FUNCTION
#################################################

async def process_inventory_message(message: InvMessage):
    try:
        data = Inventory(
            item_name= message.data.item_name,
            description= message.data.description,
            unit_price= message.data.unit_price,
            stock_in_hand= message.data.stock_in_hand,
            threshold= message.data.threshold,
            email= message.data.email
        )

        if data.stock_in_hand <= data.threshold:
            await send_inventory_alert_email(data)
            logging.info(
                f'\n!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
                f"ITEM_NAME__{data.item_name}\n"
                f"STOCK_IN_HAND: {data.stock_in_hand}\n"
                f"Threshold: {data.threshold}\n" 
                f'\n!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n')
        else:
            logging.info(f'ITEM_NAME: {data.item_name}\nENOUGH_STOCK_IN_HAND :{data.stock_in_hand}')
            
    except Exception as e:
        logging.error(f"ERROR_IN_PROCESSING_INVENTORY_MESSAGE: {str(e)}")

async def send_inventory_alert_email(data: Inventory):

    subject = "INVENTORY_ALERT"
    body = f"""
    Hello,

    NOTIFICATION:
    
    It is to inform you that

    The inventory for {data.item_name} is low. 
    Stock_in_hand: {data.stock_in_hand}
    Threshold: {data.threshold}

    Please restock as soon as possible.

    Best regards,
    Inventory Management Team
    """
    await send_email(data.email, subject, body)

