from pydantic import BaseModel
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(BaseModel):
    id: Optional[int]=None
    username: str
    email: str
    password: str
    action: str = "Signup"
    api_key: Optional[str] = None

class UserInfo(BaseModel):
    username: str
    email: str
    password: str
    
class UserListResponse(BaseModel):
    username: str
    email: str

class UserMessage(BaseModel):
    action: str
    user: User

