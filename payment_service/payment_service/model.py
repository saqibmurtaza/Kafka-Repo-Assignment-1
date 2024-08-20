from pydantic import BaseModel
from typing import Optional

class Payment(BaseModel):
    id: Optional[int] = None
    order_id: int
    amount: float
    currency: str
    payment_method: str
    status: str = "pending"

class PaymentPayload(BaseModel):
    order_id: int
    amount: float
    currency: str
    payment_method: str
