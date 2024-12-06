from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    password: str

class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    action: str = "Signup"

class LoginRequest(BaseModel):
    username: str
    email: str
    password: str
    action: str = "Login"

class Token(BaseModel):
    access_token: str
    
class UserListResponse(BaseModel):
    username: str
    email: str

class UserMessage(BaseModel):
    action: str
    user: User

class Order(BaseModel):
    id: Optional[int] = None
    item_name: str
    quantity: int
    price: float
    status: str
    user_email: str
    user_phone: str


class Inventory(BaseModel):
    id: Optional[str] = None
    item_name: str
    description: str
    unit_price: float
    stock_in_hand: int
    threshold: int  # The minimum quantity before a restock alert is triggered
    email: str  # Email to notify when the threshold is reached
    
class NotifyUser(BaseModel):
    action: str
    id: str
    username: str
    email: str
    password: str
    token: Optional[str] = None
    api_key: Optional[str] = None
    role: Optional[str] = None
