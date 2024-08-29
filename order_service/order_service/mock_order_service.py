from order_service.order_pb2 import OrderProto
from google.protobuf.json_format import ParseDict
import logging

class MockOrderService:
    def __init__(self):
        self.orders = []
    
    def create_order(self, order_data):
        order_id = len(self.orders) + 1
        order_data["id"] = order_id
        order_proto = ParseDict(order_data, OrderProto())
        self.orders.append(order_proto)
        return order_proto  # Return the order object instead of order_data
    
    def update_order(self, order_id: int, update_data):
        for my_order in self.orders:
            if my_order.id == order_id:  
                for key, value in update_data.items():
                    setattr(my_order, key, value)
                return my_order
        return None
    
    
    def track_order(self, order_id: int):
        for my_order in self.orders:
            if my_order.id == order_id:  
                return my_order
        return None
    
    def delete_order(self, order_id: int):
        for my_order in self.orders:
            if my_order.id == order_id:  
                self.orders.remove(my_order)
                return my_order
        return None
    
    def orders_list(self):
        return self.orders
