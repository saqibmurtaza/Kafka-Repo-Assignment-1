class MockOrderService:
    def __init__(self):
        self.orders = []
### Explanation

1. **Class Definition**:
    - `class MockOrderService:` defines a new class named `MockOrderService`.

2. **Constructor Method (`__init__`)**:
    - `def __init__(self):` defines the constructor method for the class. This method is called automatically when a new instance of the class is created.

3. **Initialization of `orders` Attribute**:
    - `self.orders = []` initializes an instance variable named `orders` as an empty list. The `self` keyword refers to the current instance of the class.

### Purpose

The `__init__` method ensures that every time an instance of `MockOrderService` is created, it starts with an empty list assigned to the `orders` attribute. This list is meant to hold the orders created, updated, or fetched by this mock service.

The line `order.update(update_data)` is using the built-in `update()` method of Python dictionaries.

In this context, `order` is a dictionary that represents an order, and `update_data` is another dictionary that contains the updates to be applied to the `order` dictionary.

The `update()` method takes another dictionary as an argument, and updates the current dictionary with the key-value pairs from the other dictionary. If a key already exists in the current dictionary, its value will be updated with the new value from the other dictionary. If a key does not exist in the current dictionary, it will be added with the value from the other dictionary.

Here's an example:
```
order = {'id': 1, 'status': 'pending', 'total': 100}
update_data = {'status': 'shipped', 'tracking_number': 'ABC123'}

order.update(update_data)
print(order)  # {'id': 1, 'status': 'shipped', 'total': 100, 'tracking_number': 'ABC123'}
```
As you can see, the `status` key was updated, and the `tracking_number` key was added to the `order` dictionary.

In the `update_order()` method, this means that the `order` dictionary is updated with the new values from the `update_data` dictionary. If the `update_data` dictionary contains new keys, they will be added to the `order` dictionary. If it contains updated values for existing keys, they will be updated accordingly.

For example, if `order` is `{'id': 1, 'status': 'pending', 'total': 100}` and `update_data` is `{'status': 'shipped', 'notes': 'Thanks for your order!'}`, the resulting `order` dictionary would be `{'id': 1, 'status': 'shipped', 'total': 100, 'notes': 'Thanks for your order!'}`.

notification_payload = NotificationPayload(
        order_id=created_order.id,
        status="created",
        user_email="saqibmurtazakhan@gmail.com",
        user_phone="+923171938567"
    )
async def send_notification(
        payload: NotificationPayload, 
        producer: AIOKafkaProducer,
        topic: str = settings.TOPIC_ORDER_STATUS):
    await producer.start()
    try:
        payload_proto = NotificationPayloadProto(
            order_id=payload.order_id,
            status=payload.status,
            user_email=payload.user_email,
            user_phone=payload.user_phone
        )
        message = payload_proto.SerializeToString()
        await producer.send_and_wait(topic, message)
        logging.info(f"NOTIFICATION_SENT_TO {payload.order_id, payload.user_email}")
    finally:
        await producer.stop()
