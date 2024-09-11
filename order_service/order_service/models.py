from pydantic import BaseModel
from typing import Optional
from sqlmodel import SQLModel, Field

class Order(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    item_name: str
    quantity: int
    price: float
    status: str
    user_email: str
    user_phone: str
    api_key: str= None
    source: str

class MockOrder(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    item_name: str
    quantity: int
    price: float
    status: str
    user_email: str
    user_phone: str
    api_key: str= None
    source: str

class OrderCreated(BaseModel):
    item_name: str
    quantity: int
    price: float
    status: str
    user_email: str
    user_phone: str
    api_key: str= None

class MockTable:
    def __init__(self, data):
        self._data = data  # Use a private variable to hold the data
        self.filtered_data = data  # Initialize filtered data to be the same as input data

    @property
    def data(self):
        return self.filtered_data

    def select(self, *args, **kwargs):
        return self

    # Filter data based on column and value, 
    # assuming data is a list of dictionaries
    def eq(self, column_name, value):
        # Directly access attributes of OrderProto
        self.filtered_data = [item for item in self._data if getattr(item, column_name) == value]
        return self

    def execute(self):
        return self


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