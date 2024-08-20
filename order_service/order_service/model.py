from pydantic import BaseModel
from typing import Optional

class Order(BaseModel):
    id: Optional[int] = None
    item_name: str
    quantity: int
    price: float
    status: str= "pending"

class OrderCreated(BaseModel):
    item_name: str
    quantity: int
    price: float
    status: str= "pending"


class NotificationPayload(BaseModel):
    order_id: int
    status: str
    user_email: str
    user_phone: str
