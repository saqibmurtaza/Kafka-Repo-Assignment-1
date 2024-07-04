from pydantic import BaseModel, Field
from typing import Optional

class Inventory(BaseModel):
    id: Optional[int]= None
    item: str
    stock_in_hand: int 
    unit_price: float
    
    @property
    def stock_value(self) -> float:
        return self.stock_in_hand * self.unit_price
        
class InventoryResponse(BaseModel):
    id: Optional[int]= None
    item: str
    stock_in_hand: int 
    unit_price: float
    stock_value: Optional[float] = Field(default=None, readOnly= True)


