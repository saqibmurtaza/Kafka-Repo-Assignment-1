from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from typing import Optional

class Inventory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_name: str
    description: str
    unit_price: float
    quantity: int
    stock_in_hand: int
    threshold: int  # The minimum quantity before a restock alert is triggered
    email: str  # Email to notify when the threshold is reached

    @property
    def stock_value(self) -> float:
        return self.stock_in_hand * self.unit_price

class InventoryUpdate(BaseModel):
    item_name: str
    description: str
    unit_price: float
    quantity: int
    stock_in_hand: int
    threshold: int  # The minimum quantity before a restock alert is triggered
    email: str  # Email to notify when the threshold is reached


class User(BaseModel):
    id: Optional[int]=None
    username: str
    email: str
    password: str

