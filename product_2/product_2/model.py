from sqlmodel import SQLModel, Field
from typing import Optional

class Product(SQLModel, table=True):
    __tablename__ = "catalogue"
    id: Optional[int] = Field(default=None, primary_key=True)
    product_name : str
    description: str
    price : float
    quantity : int
