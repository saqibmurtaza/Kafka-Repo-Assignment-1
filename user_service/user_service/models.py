from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Real User model
class User(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    api_key: Optional[str] = None
    source: str = Field(default="real")  # Add this column to distinguish entries

# Mock User model
class MockUser(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    api_key: Optional[str] = None
    source: str = Field(default="mock")

class NotifyUser(BaseModel):
    action: str
    id: str
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

class UserMessage(BaseModel):
    action: str
    user: User

class MockTable:
    def __init__(self, data):
        self._data = data  # Use a private variable to hold the data
        self.filtered_data = data  # Initialize filtered data to be the same as input data

    @property
    def data(self):
        return self.filtered_data

    def select(self, *args, **kwargs):
        return self


    def eq(self, column_name, value):
        self.filtered_data = [item for item in self._data if item.get(column_name) == value]
        return self

    def execute(self):
        return self
