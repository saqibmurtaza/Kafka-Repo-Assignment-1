from fastapi import HTTPException
from aiokafka import AIOKafkaConsumer
from .inventory_pb2 import Inventory as InvProto, InventoryUpdates as InvMessage
from .order_pb2 import OrderProto
from .settings import settings
from .notify_orderservice import process_order_message
from .notify_userservice import process_user_message, send_profile_email
from .notify_invservice import process_inventory_message
import asyncio, json, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def consume():
    consumer = AIOKafkaConsumer(
        settings.TOPIC_USER_EVENTS,
        settings.TOPIC_ORDER_STATUS,
        settings.TOPIC_NOTIFY_INVENTORY,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        group_id=settings.CONSUMER_GROUP_NOTIFY_MANAGER
    )
    await consumer.start()
    try:
        async for msg in consumer:
            logging.info(f'RECEIVED_MSG_IN_CONSUMER:{msg}')
            topic= msg.topic

            if topic == settings.TOPIC_USER_EVENTS:
                # Decode received messages
                decoded_json_msg= msg.value.decode('utf-8') # from bytes to json_formated string
                payload_dict= json.loads(decoded_json_msg) # from string to dict
                if 'get_user_profile' in payload_dict:
                    await send_profile_email(payload_dict)
                await process_user_message(payload_dict)

            elif topic == settings.TOPIC_ORDER_STATUS:
                
                decoded_order_msg= OrderProto()
                decoded_order_msg.ParseFromString(msg.value)
        # FUNCTION_CALL
                await process_order_message(decoded_order_msg)
            
            elif topic == settings.TOPIC_NOTIFY_INVENTORY:

                decoded_inv_msg= InvMessage()
                decoded_inv_msg.ParseFromString(msg.value)
                logging.info(f'DECODED_INV_MSG : {decoded_inv_msg}')
                
                await process_inventory_message(decoded_inv_msg)
   
    except Exception as e:
        logging.error(f"FAILED_TO_PROCESS_RECIEVED_MESSAGE: {e}")

    finally:
        await consumer.stop()

async def start_consumer():
    logging.info('CONSUMER STARTED ---------------------------------------------------------------')
    loop = asyncio.get_event_loop()
    loop.create_task(consume())
