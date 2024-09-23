from fastapi import FastAPI
from contextlib import asynccontextmanager
from .consumer import start_consumer
from .settings import settings
import logging, asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    consumer_task= asyncio.create_task(
        start_consumer(
            topic=settings.TOPIC_ORDER_STATUS,
            bootstrap_server=settings.BOOTSTRAP_SERVER,
            consumer_group_id=settings.CONSUMER_GROUP_PAYMENT_EVENTS))
    try:
        yield
    finally:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Consumer task cancelled successfully")

app = FastAPI(
    lifespan=lifespan,
    title='PAYMENT_SERVICE',
    servers=[
        {
            "url": "http://localhost:8012",
            "description": "Server: Uvicorn, port: 8012"
        }
    ]
)

@app.get("/")
def read_root():
    return {"message": "Payment Service is running"}

