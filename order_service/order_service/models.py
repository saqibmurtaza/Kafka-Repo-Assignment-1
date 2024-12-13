from pydantic import BaseModel
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid

class CartPayload(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    item_name: str
    quantity: int

class Cart(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    item_name: str
    description: str
    quantity: int
    price: float
    payment_status: str
    user_email: str


class MockCart(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    item_name: str
    description: str
    quantity: int
    price: float
    payment_status: str
    user_email: str

class OrderCreate(BaseModel):
    id: int # id is int in db_table_catalaoue, so keep int
    quantity: int
    user_email: str
    payment_status: str

class OrderUpdate(BaseModel):
    # id: str # id is str in db_table_mockorder, so keep str
    quantity: int
    user_email: str
    payment_status: str


class OrderStatusUpdate(BaseModel):
    order_id: str
    status: str

# MOCK SETUP

class MockOrderService:
    def __init__(self):
        self.orders = []
    
    def table(self, name:str):
        if name == 'mock_order':
            return MockTable(self.orders)
        raise ValueError(f"NO_MOCK_TABLE_FOR_NAME {name}")

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
        # Directly access attributes of OrderProto
        self.filtered_data = [item for item in self._data if getattr(item, column_name) == value]
        return self

    def execute(self):
        return self


# class OrderStatus:
#     PENDING = "pending"
#     CONFIRMED = "confirmed"
#     PROCESSING = "processing"
#     SHIPPED = "shipped"
#     DELIVERED = "delivered"
#     CANCELED = "canceled"
#     REFUNDED = "refunded"

# ORDER_STATUS
# PENDING
# CONFIRMED
# PROCESSING
# SHIPPED
# DELIVERED
# CANCELED
# REFUNDED

# ORDER_STATUS_FLOW:
# 1. Order Placed: Order is created and initially set to "PENDING".
# 2. Payment Verification: If payment is required, the status might change to "CONFIRMED"
#    once the payment is successful.
# 3. Fulfillment: Order moves to "PROCESSING" as it is prepared for shipment.
# 4. Shipping: Once shipped, the status changes to "SHIPPED".
# 5. Delivery: On successful delivery, the status is updated to "DELIVERED".
# 6. Cancellation/Return: If the order is canceled or returned, the status changes to "CANCELED" or "RETURN".
# 7. Refund Processing: If a refund is processed, the status changes to "REFUNDED".