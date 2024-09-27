from aiokafka import AIOKafkaProducer
from .settings import settings

async def send_message(message,topic,bootstrap_server, 
        ):
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_server)
    await producer.start()
    try:

        await producer.send_and_wait(topic, message)
    
    finally:
        await producer.stop()