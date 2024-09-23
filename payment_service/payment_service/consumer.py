from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from .order_pb2 import OrderProto
from .notify_logic import handle_notifications
from .pay_process import process_payment
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
        bootstrap_servers= bootstrap_server,
        group_id= consumer_group_id        
    )
    while True:
        try:
            await consumer.start()
            logging.info('CONSUMER STARTED -________--------------------------')
            break
        except KafkaConnectionError as e:
            logging.error(f'CONSUMER STARTUP FAILED {e}, Retry in 5 seconds')
            await asyncio.sleep(5)
    try:
        async for message in consumer:
            # Deserialize the protobuf message
            msg_in_consumer= OrderProto() #<---Check Note @ End_Of_Code
            msg_in_consumer.ParseFromString(message.value)
            logging.info(f"RECD_MESSAGE_IN_CONSUMER:\n {msg_in_consumer}")

            # CALL_FUNCTION_TO_RETURN_STATUS_OF_PAYMENT
            status_message= await process_payment(msg_in_consumer)        
    
            # CALL_FUNCTION_TO_NOTIFY_ORDER_SERVICE_FOR_PAY_STATUS
            await handle_notifications(msg_in_consumer, status_message)
            logging.info(
                f"\n*********PAYMENT_PROCESS_COMPLETE*********\n"
                f"*********STATUS: {status_message}****************\n"
                )

    except Exception as e:
        logger.error(f"ERROR_IN_PROCESSING_MSSG, **ERROR**: {str(e)}")

    finally:
        logging.info("***************Consumer stopped")
        await consumer.stop()  # Ensure the consumer stops gracefully
    
'''
Note:
The ParseFromString method populates the msg_in_consumer instance 
with data from the Kafka message. This means that after this line
(msg_in_consumer.ParseFromString(message.value), 
msg_in_consumer holds the deserialized data, 
while deserialized_message is usually None
'''