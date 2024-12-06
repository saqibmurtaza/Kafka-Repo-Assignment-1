from fastapi import HTTPException
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from .inventory_pb2 import Inventory as InvProto, InventoryUpdates as InvMessage
from .order_pb2 import OrderProto
from .settings import settings
from .notify_orderservice import process_order_message
from .notify_userservice import send_signup_email, send_login_email, send_profile_email
from .notify_invservice import process_inventory_message
import asyncio, json, logging, traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_consumer(topic, bootstrap_server, consumer_group_id ):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_server,
        group_id=consumer_group_id
    )
    # Retry mechanism to keep up the consumer
    while True:
        try:
            await consumer.start()
            logging.info('CONSUMER STARTED')
            break
        except KafkaConnectionError as e:
            logging.error(f'CONSUMER STARTUP FAILED {e}, Retry in 5 seconds')
            await asyncio.sleep(5)    
    try:
        async for msg in consumer:
            logging.info(f'RECEIVED_MSG_IN_CONSUMER:{msg}')
            topic= msg.topic

            if topic == settings.TOPIC_USER_EVENTS:
                # Decode received messages
                decoded_json_msg= msg.value.decode('utf-8') # from bytes to json_formated string
                payload_list= json.loads(decoded_json_msg) # from string to dict

                # Check if payload_list is a dictionary (Signup or login case)
                if isinstance(payload_list, dict):
                    action = payload_list.get('action')

                    if action == 'Signup':
                        await send_signup_email(payload_list)
                    elif action == 'login':
                        await send_login_email(payload_list)

                    elif isinstance(payload_list, list):
                        if any(item.get('action') == 'get_user_profile' for item in payload_list):
                            logging.info("Found get_user_profile action in list")       
                            user_list= []    
                            for my_list in payload_list:
                                if my_list.get('action') == 'get_user_profile':
                                    user_list.append(my_list)
                                    await send_profile_email(user_list)

            elif topic == settings.TOPIC_ORDER_STATUS:
                decoded_order_msg= OrderProto()
                decoded_order_msg.ParseFromString(msg.value)

        # FUNCTION_CALL
                await process_order_message(decoded_order_msg)
            
            elif topic == settings.TOPIC_NOTIFY_INVENTORY:
                decoded_inv_msg= InvMessage()
                decoded_inv_msg.ParseFromString(msg.value)
        
        # FUNCTION_CALL FOR EMAILS
                await process_inventory_message(decoded_inv_msg)
   
    except asyncio.CancelledError:
        logger.info("CONSUMER_TASK_CANCELLED")
    except Exception as e:
        logger.error(f"ERROR_IN_PROCESSING_MSSG: {msg.value}, ERROR: {str(e)}")

    finally:
        await consumer.stop()
