from pydantic import BaseModel
from typing import Optional

class Order(BaseModel):
    id: Optional[int] = None
    item_name: str
    quantity: int
    price: float
    status: str= "pending"
