import logging
from fastapi import FastAPI
from .consumer import consume

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='Notification Service',
    servers=[
        {
            "url": "http://localhost:8010",
            "description": "Server: Uvicorn, port: 8010"
        }
    ]
)

@app.on_event("startup")
async def startup_event():
    await consume()

@app.get("/")
def read_root():
    return {"message": "Notification Service is running"}
