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
    status: str= "pending"
    user_email: str
    user_phone: str


from pydantic import BaseModel
from typing import Optional

class Inventory(BaseModel):
    id: Optional[int] = None
    item_name: str
    quantity: int
    threshold: int  # The minimum quantity before a restock alert is triggered
    email: str  # Email to notify when the threshold is reached
