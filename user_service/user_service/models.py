from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Real User model
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    api_key: Optional[str] = None
    source: str = Field(default="real")  # Add this column to distinguish entries

# Mock User model
class MockUser(SQLModel, table=True):
    __tablename__ = 'mock_user'  # Explicitly name the table 'mock_user'
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    api_key: Optional[str] = None
    source: str = Field(default="mock")

class NotifyUser(BaseModel):
    action: str
    id: Optional[int]=None
    username: str
    email: str
    password: str
    api_key: Optional[str] = None

class UserInfo(BaseModel):
    username: str
    email: str
    password: str

class LoginInfo(BaseModel):
    email: str
    password: str
   
class UserListResponse(BaseModel):
    username: str
    email: str

class UserMessage(BaseModel):
    action: str
    user: User
