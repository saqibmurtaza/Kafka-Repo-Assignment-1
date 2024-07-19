# from fastapi import FastAPI
# from contextlib import asynccontextmanager
# from pydantic import BaseModel
# from notification_service import settings
# from .consumer import start_consumer, notify_order_status, NotificationPayload
# from .notifyme_service import NotificationService
# import logging, asyncio

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     topics = [settings.TOPIC_ORDER_STATUS, settings.TOPIC_USER_EVENTS]
#     consumer_task = asyncio.create_task(
#         start_consumer(
#             topics,
#             bootstrap_server=settings.BOOTSTRAP_SERVER,
#             consumer_group_id=settings.CONSUMER_GROUP_NOTIFYME_MANAGER
#         )
#     )
#     try:
#         yield
#     except Exception as e:
#         logger.error(f"An error occurred in lifespan context manager: {e}")
#     finally:
#         consumer_task.cancel()
#         try:
#             await consumer_task
#         except asyncio.CancelledError:
#             logger.info("Consumer task cancelled")

# app = FastAPI(
#     lifespan=lifespan,
#     title='Notification Service',
#     servers=[
#         {
#             "url": "http://localhost:8002",
#             "description": "Server: Uvicorn, port: 8002"
#         }
#     ]
# )

# @app.get("/")
# def read_root():
#     return {"message": "Notification Service"}

# @app.post("/manual_notifications/notify/order/status")
# async def manual_notifications(payload: NotificationPayload ):
#     notify= await notify_order_status(payload)
#     return notify

from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel
from notification_service import settings
from .consumer import start_consumer, notify_order_status, NotificationPayload
import logging, asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    topics = [settings.TOPIC_ORDER_STATUS, settings.TOPIC_USER_EVENTS]
    consumer_task = asyncio.create_task(
        start_consumer(
            topics,
            bootstrap_server=settings.BOOTSTRAP_SERVER,
            consumer_group_id=settings.CONSUMER_GROUP_NOTIFYME_MANAGER
        )
    )
    try:
        yield
    except Exception as e:
        logger.error(f"An error occurred in lifespan context manager: {e}")
    finally:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Consumer task cancelled")

app = FastAPI(
    lifespan=lifespan,
    title='ShopSphere _ Notification Service',
    servers=[
        {
            "url": "http://localhost:8002",
            "description": "Server: Uvicorn, port: 8002"
        }
    ]
)

@app.get("/")
def read_root():
    return {"message": "Notification Service"}

@app.post("/manual_notifications/notify/order/status")
async def manual_notifications(payload: NotificationPayload):
    notify = await notify_order_status(payload)
    return notify
