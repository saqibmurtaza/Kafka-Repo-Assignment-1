from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from aiokafka import AIOKafkaProducer
from .producer import get_kafka_producer
from .dependencies import get_payfast_service, get_stripe_service
from .model import Payment, PaymentPayload
from .payment_pb2 import PaymentNotificationProto
from .settings import settings
import os, logging, asyncio
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting Payment Service...')
    try:
        yield
    finally:
        logger.info('Shutting down Payment Service...')

app = FastAPI(
    lifespan=lifespan,
    title="SaqibShopSphere _ Payment Service",
    servers=[
        {
            "url": "http://localhost:8012",
            "description": "Server: Uvicorn, port: 8012"
        }
    ],
)

def get_payment_service(payment_method: str):
    if payment_method == "payfast":
        return get_payfast_service()
    elif payment_method == "stripe":
        return get_stripe_service()
    else:
        raise HTTPException(status_code=400, detail="Unsupported payment method")

async def send_payment_notification(
        payload: PaymentPayload, 
        producer: AIOKafkaProducer,
        topic: str = settings.TOPIC_PAYMENT_EVENTS):
    await producer.start()
    try:
        payload_proto = PaymentNotificationProto(
            order_id=payload.order_id,
            amount=payload.amount,
            currency=payload.currency,
            payment_method=payload.payment_method
        )
        message = payload_proto.SerializeToString()
        await producer.send_and_wait(topic, message)
        logger.info(f"Payment notification sent for order_id {payload.order_id}")
    finally:
        await producer.stop()

@app.get("/")
def read_root():
    return {"message": "Payment Service for Saqib's online mart"}

@app.post("/payments", response_model=Payment)
async def process_payment(
    payment: PaymentPayload,
    producer: AIOKafkaProducer = Depends(get_kafka_producer)
):
    payment_service = get_payment_service(payment.payment_method)
    payment_status = await payment_service.process_payment(payment.amount, payment.currency, payment.order_id)

    if payment_status:
        payment_record = Payment(
            order_id=payment.order_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_method=payment.payment_method,
            status="completed"
        )
        await send_payment_notification(payment, producer)
        return payment_record
    else:
        raise HTTPException(status_code=500, detail="Payment processing failed")

@app.get("/payments", response_model=List[Payment])
async def get_payments_list(service = Depends(get_payment_service)):
    return service.payments_list()
