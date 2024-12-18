from fastapi import HTTPException
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from sqlmodel import select
from .database import engine, Session
from .settings import settings
from .models import Inventory
from .notify_logic import send_message, send_batch_inventory_list
from .inventory_pb2 import Inventory as InvProto, InventoryUpdates as MsgInv
from .database import supabase
from uuid import uuid4
import logging, asyncio, json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_consumer(
        topic, 
        bootstrap_server, 
        consumer_group_id
):
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
        async for message in consumer:
            msg_in_consumer = MsgInv()
            msg_in_consumer.ParseFromString(message.value)

            operation = msg_in_consumer.operation
            invproto = msg_in_consumer.data
            
            with Session(engine) as session:
                if operation == "add":
                    inventory_id = invproto.id
                    if not inventory_id:
                        logging.warning("Received inventory with id=0, attempting to auto-generate id")
                        inventory_id = str(uuid4()) # Set to None to allow auto-generation
                    
                    # Check if the inventory already exists to prevent duplicate insertion
                    existing_inventory = session.get(Inventory, inventory_id)
                    if existing_inventory:
                        logging.info(f"Inventory with ID {inventory_id} already exists. Skipping insertion.")
                        await consumer.commit()  # Manually commit offset to avoid re-processing
                        continue
                        
                    inventory_data = Inventory(
                        id=inventory_id, 
                        item_name=invproto.item_name,
                        description=invproto.description,
                        unit_price=invproto.unit_price,
                        stock_in_hand=invproto.stock_in_hand,
                        threshold=invproto.threshold,
                        email=invproto.email
                    )
                    
                    try:
                        session.add(inventory_data)
                        session.commit()
                        session.refresh(inventory_data)
                        logging.info(
                            f"***********************\nADDED_INVENTORY:\n"
                            f"{inventory_data}\n***********************\n"
                            )

            # ENCODE_MESSAGE_TO_PROTOBUF
                        msg_response = MsgInv(
                            operation="add",
                            data=InvProto(
                                id=inventory_data.id,
                                item_name=inventory_data.item_name,
                                unit_price=inventory_data.unit_price,
                                stock_in_hand=inventory_data.stock_in_hand,
                                threshold=inventory_data.threshold,
                                description=inventory_data.description,
                                email=inventory_data.email
                            )
                        )
                        msg_response_bytes = msg_response.SerializeToString()
    
                    #FUNCTION_CALL
                        await send_message(msg_response_bytes, topic=settings.TOPIC_NOTIFY_INVENTORY, bootstrap_server=settings.BOOTSTRAP_SERVER)

                        logging.info(f'MSG_SENT_TO_NOTIFICATION_SERVICE_TOPIC_NOTIFY_MANGER')
                        await consumer.commit()  # Commit offset after successful processing
                        
                    except Exception as e:
                        session.rollback()
                        logging.error(f"AN_ERROR_OCCURED_IN_CONSUMER: {inventory_data}, ERROR: {str(e)}")
                
                elif operation == "delete":
                    inventory_id = invproto.id
                    inv_data = session.get(Inventory, inventory_id )
                    if inv_data:
                        session.delete(inv_data)
                        session.commit()
                        logging.info(
                            f"*******************************\nDELETED INVENTORY_OF_ID : "
                            f"{inventory_id}\n*******************************\n"
                            )
                    else:
                        logging.warning(f"INVENTORY_WITH_ID: {inventory_id} NOT_FOUND_TO_DELETE")

                elif operation == "read":
                    inventory_id = invproto.id
                    inv_data = session.get(Inventory, inventory_id)
                    if inv_data:
                        logging.info(
                            f"*******************************TRACKED_INVENTORY\n"
                            f"{inv_data}\n*******************************\n"
                            )
                    else:
                        logging.warning(f"TRACKED_ID: {inventory_id} NOT_FOUND")

                elif operation == "update":
                    inventory_id = invproto.id
                    product = session.get(Inventory, inventory_id)
                    if product:
                        product.item_name = invproto.item_name
                        product.unit_price = invproto.unit_price
                        product.stock_in_hand= invproto.stock_in_hand
                        product.threshold= invproto.threshold
                        product.description = invproto.description
                        product.email = invproto.email
                        session.commit()
                        session.refresh(product)
                        logging.info(
                            f"***********************\nUPDATED_INVENTORY_INFO\n"
                            f"{product}\n***********************\n"
                            )
                    else:
                        logging.warning(f"INVENTORY_ID: {inventory_id} NOT_FOUND_TO_UPDATE")
                    
                    """
                    Prepare Message for sending to Notification Service
                    ENCODE_MESSAGE_TO_PROTOBUF
                    """
                    message = MsgInv(
                        operation="update",
                        data=InvProto(
                            item_name=product.item_name,
                            unit_price=product.unit_price,
                            stock_in_hand=product.stock_in_hand,
                            threshold=product.threshold,
                            description=product.description,
                            email=product.email
                        )
                    )
                    message_bytes = message.SerializeToString()
    
                    # Function Call to Sent Notifications
                    await send_message(message_bytes,topic=settings.TOPIC_NOTIFY_INVENTORY, bootstrap_server=bootstrap_server)

                elif operation == 'list':
                    # Fetch all products from the database
                    inventory= supabase.from_('inventory').select('*').execute()
                    inventory_json= inventory.json()
                    inventory_dict= json.loads(inventory_json)
                    inv_data= inventory_dict.get('data')

                    pretty_format= json.dumps(inv_data, indent=4)
                    logging.info(f"PRETTY FORMAT : {pretty_format}")

                    # Serialized & send to Notification service
                    notify_inv_list= [] # initiate empty list
                    for my_inv in inv_data:
                        inv_proto= InvProto(
                            id=my_inv['id'], 
                            item_name=my_inv['item_name'],
                            description=my_inv['description'],
                            unit_price=my_inv['unit_price'],
                            stock_in_hand=my_inv['stock_in_hand'],
                            threshold=my_inv['threshold'],
                            email=my_inv['email']
                        )
                        # Prepare message
                        message= MsgInv(operation="view", data=inv_proto)
                        notify_inv_list.append(message)
                    
                    # Function Call
                    logging.info(f"MESSAGE SENDING.....")
                    await send_batch_inventory_list(notify_inv_list)
                    logging.info(f"INVENTORY_LIST_SENT_TO_NOTIFICATION_SERVICE.....")

    except asyncio.CancelledError:
        logger.info("CONSUMER_TASK_CANCELLED")
    except Exception as e:
        logger.error(f"ERROR_IN_PROCESSING_MSSG_IN_CONSUMER, ERROR: {str(e)}")

    finally:
        await consumer.stop()
