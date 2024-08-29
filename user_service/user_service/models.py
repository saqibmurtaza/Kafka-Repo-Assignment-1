from pydantic import BaseModel
from typing import Optional
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(BaseModel):
    id: Optional[int]=None
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

class ActionEnum(Enum):
    LOGIN = "login"
    SIGNUP = "signup"

