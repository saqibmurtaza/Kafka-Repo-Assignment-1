from pydantic import BaseModel
from typing import Optional

class Order(BaseModel):
    id: Optional[int] = None
    item_name: str
    quantity: int
    price: float
    status: str= "pending"

class OrderCreated(BaseModel):
    item_name: str
    quantity: int
    price: float
    status: str= "pending"


class NotificationPayload(BaseModel):
    # order_id: int
    status: str
    user_email: str
    user_phone: str
    # action: str

# ORDER_STATUS_FLOW:
# 1. Order Placed: Order is created and initially set to "PENDING".
# 2. Payment Verification: If payment is required, the status might change to "CONFIRMED" once the payment is successful.
# 3. Fulfillment: Order moves to "PROCESSING" as it is prepared for shipment.
# 4. Shipping: Once shipped, the status changes to "SHIPPED".
# 5. Delivery: On successful delivery, the status is updated to "DELIVERED".
# 6. Cancellation/Return: If the order is canceled or returned, the status changes to "CANCELED" or "RETURN".
# 7. Refund Processing: If a refund is processed, the status changes to "REFUNDED".