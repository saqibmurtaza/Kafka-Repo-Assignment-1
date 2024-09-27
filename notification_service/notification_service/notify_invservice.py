from .models import Inventory
from .inventory_pb2 import InventoryUpdates as InvMessage
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
            quantity= message.data.quantity,
            stock_in_hand= message.data.stock_in_hand,
            threshold= message.data.threshold,
            email= message.data.email
        )
        if data.stock_in_hand <= data.threshold:
            await send_inventory_alert_email(data)
            logging.info(
                f'\n!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
                f"ITEM_NAME__{data.item_name}\n"
                f"CURRENT_QTY: {data.quantity}\n"
                f"STOCK_IN_HAND: {data.stock_in_hand}\n"
                f"Threshold: {data.threshold}\n" 
                f'\n!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n')
        else:
            logging.info(f'ENOUGH_STOCK_IN_HAND :{data.stock_in_hand}')
            
    except json.JSONDecodeError as e:
        logging.error(f"FAILED_TO_DECODE_MESSAGE: {e}")

async def send_inventory_alert_email(data: Inventory):

    ADMIN_EMAILS = ["saqibmurtaza@yahoo.com", "saqibmurtaza@hotmail.com"]
    
    if data.email in ADMIN_EMAILS:

        subject = "Inventory Alert"
        body = f"""
        Hello,

        The inventory for {data.item_name} is low. 
        Current quantity: {data.quantity}.

        Please restock as soon as possible.

        Best regards,
        Inventory Management Team
        """
        await send_email(data.email, subject, body)
    
    else:
        logging.info(
            f'\n!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
            f'YOU_ARE_NOT_ADMIN\n'
            f'INVENTORY_THRESHOLD_EMAILS__SENT_TO_ADMINS_ONLY\n'
            f'!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!!****!\n'
            )
