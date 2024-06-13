from sqlmodel import SQLModel, Field, Session, create_engine
from typing import Optional

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_name : str
    description: str
    price : float
