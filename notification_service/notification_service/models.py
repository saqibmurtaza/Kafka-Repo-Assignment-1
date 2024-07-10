from pydantic import BaseModel

class NotificationPayload(BaseModel):
    order_id: int
    status: str
    user_email: str
    user_phone: str

class User(BaseModel):
    id: int
    username: str
    email: str
    password: str
    phone: str= None

class UserMessage(BaseModel):
    action: str
    user: User
