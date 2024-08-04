from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from typing import Optional, List

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_name : str
    description: str
    price : float

class DeleteProductsRequest(BaseModel):
    ids: List[int]

class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
