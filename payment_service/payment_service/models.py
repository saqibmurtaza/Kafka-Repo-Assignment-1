from pydantic import BaseModel
from typing import Optional
from sqlmodel import SQLModel, Field

class Order(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    item_name: str
    quantity: int
    price: float
    status: str
    user_email: str
    user_phone: str
    api_key: str= None


class MockOrder(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    item_name: str
    quantity: int
    price: float
    status: str
    user_email: str
    user_phone: str
    api_key: str= None

class PaymentPayload(BaseModel):
    id: str
    amount: float
    currency: str= 'usd'
    payment_method: str


# PAYMENT_STATUS

# PENDING
# CONFIRMED
# FAILED
# REFUNDED

# PAYMENT_STATUS_FLOW:
# 1. Payment Initiated: Payment is created and initially set to "PENDING".
# 2. Payment Verification: If payment is successful, the status changes to "CONFIRMED".
# 3. Payment Failed: If payment fails, the status changes to "FAILED".
# 4. Refund Processing: If a refund is processed, the status changes to "REFUNDED".
