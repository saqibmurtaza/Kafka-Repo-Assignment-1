from contextlib import asynccontextmanager
from fastapi import FastAPI
from .consumer import start_consumer
from .settings import settings
import logging, asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    consumer_task_user= asyncio.create_task(
        start_consumer(
            topic=settings.TOPIC_USER_EVENTS,
            bootstrap_server=settings.BOOTSTRAP_SERVER,
            consumer_group_id=settings.CONSUMER_GROUP_NOTIFY_MANAGER))

    consumer_task_order = asyncio.create_task(
        start_consumer(
            topic=settings.TOPIC_ORDER_STATUS,
            bootstrap_server=settings.BOOTSTRAP_SERVER,
            consumer_group_id=settings.CONSUMER_GROUP_NOTIFY_MANAGER
        )
    )
    consumer_task_inventory = asyncio.create_task(
        start_consumer(
            topic=settings.TOPIC_NOTIFY_INVENTORY,
            bootstrap_server=settings.BOOTSTRAP_SERVER,
            consumer_group_id=settings.CONSUMER_GROUP_NOTIFY_MANAGER
        )
    )
    
    try:
        yield
    finally:
        # Proper cancellation and waiting
        for task in [consumer_task_user, consumer_task_order, consumer_task_inventory]:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logging.info(f"Task {task} cancelled successfully")
                pass

app = FastAPI(
    lifespan=lifespan,
    title='Notification Service',
    servers=[
        {
            "url": "http://localhost:8010",
            "description": "Server: Uvicorn, port: 8010"
        }
    ]
)


@app.get("/")
def read_root():
    return {"message": "Notification Service is running"}
