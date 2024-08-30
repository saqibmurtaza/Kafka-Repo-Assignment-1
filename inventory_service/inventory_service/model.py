from pydantic import BaseModel, Field
from typing import Optional

class Inventory(BaseModel):
    id: Optional[int] = None
    item_name: str
    quantity: int
    threshold: int  # The minimum quantity before a restock alert is triggered
    email: str  # Email to notify when the threshold is reached

class InventoryCreate(BaseModel):
    item_name: str
    quantity: int
    threshold: int
    email: str
    stock_in_hand: int
    unit_price: float


    @property
    def stock_value(self) -> float:
        return self.stock_in_hand * self.unit_price

class InventoryResponse(BaseModel):
    id: Optional[int]
    item_name: str
    quantity: int
    threshold: int
    email: str
    stock_in_hand: int
    unit_price: float
    stock_value: float

