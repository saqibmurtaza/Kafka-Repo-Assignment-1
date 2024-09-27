from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from sqlmodel import select
from .database import engine, Session
from .settings import settings
from .models import Inventory
from .send_msg import send_message
from .inventory_pb2 import Inventory as InvProto, InventoryUpdates as MsgInv
import logging, asyncio

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
                    if inventory_id == 0:
                        logging.warning("Received inventory with id=0, attempting to auto-generate id")
                    
                    inventory_data = Inventory(
                        id=inventory_id if inventory_id != 0 else None,  # Let the database generate id if it's 0
                        item_name=invproto.item_name,
                        description=invproto.description,
                        unit_price=invproto.unit_price,
                        quantity=invproto.quantity,
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

            # # ENCODE_MESSAGE_TO_PROTOBUF
                        msg_response = MsgInv(
                            operation="add",
                            data=InvProto(
                                id=inventory_data.id,
                                item_name=inventory_data.item_name,
                                unit_price=inventory_data.unit_price,
                                quantity=inventory_data.quantity,
                                stock_in_hand=inventory_data.stock_in_hand,
                                threshold=inventory_data.threshold,
                                description=inventory_data.description,
                                email=inventory_data.email
                            )
                        )
                        msg_response_bytes = msg_response.SerializeToString()
    
            #FUNCTION_CALL
                        await send_message(msg_response_bytes, topic=settings.TOPIC_NOTIFY_INVENTORY, bootstrap_server=settings.BOOTSTRAP_SERVER)

                        logging.info(f'MSG_SENT_TO_TOPIC_NOTIFY_MANGER')
                        
                    except Exception as e:
                        session.rollback()
                        logging.error(f"AN_ERROR_OCCURED: {inventory_data}, ERROR: {str(e)}")
                
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
                        product.quantity= invproto.quantity
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

                elif operation == "list":
                        # Fetch all products from the database
                        inventory = session.exec(select(Inventory)).all()
                        logging.info(
                            f"***********************\nRETRIEVED_INVENTORY"
                            f"{inventory}\n***********************\n"
                            )

    except asyncio.CancelledError:
        logger.info("CONSUMER_TASK_CANCELLED")
    except Exception as e:
        logger.error(f"ERROR_IN_PROCESSING_MSSG: {message.value}, ERROR: {str(e)}")
    finally:
        await consumer.stop()
