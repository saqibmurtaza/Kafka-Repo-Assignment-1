import logging

class MockOrderService:
    def __init__(self):
        self.orders= []
    
    def create_order(self, order_data):
        order_id= len(self.orders)+1
        order_data["id"]= order_id
        self.orders.append(order_data)
        return order_data
    
    def update_order(self, order_id:int, update_data):
        for my_order in self.orders:
            if my_order["id"] == order_id:
                my_order.update(update_data)
                return my_order
        return None
    
    def track_order(self, order_id:int):
        for my_order in self.orders:
            if my_order["id"] == order_id:
                return my_order
        return None
    
    def delete_order(self, order_id:int):
        for my_order in self.orders:
            if my_order["id"] == order_id:
                self.orders.remove(my_order)
                return my_order
        return None
    
    def orders_list(self):
        return self.orders
                