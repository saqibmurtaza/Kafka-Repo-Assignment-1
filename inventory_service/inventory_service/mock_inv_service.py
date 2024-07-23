from .model import Inventory

class MockInventoryService:
    def __init__(self):
        self.inventory= []
    
    def create_inventory(self, item_data:Inventory):
        item_data["id"]= len(self.inventory) + 1
        item_data["stock_value"] = item_data["stock_in_hand"] * item_data["unit_price"]
        self.inventory.append(item_data)
        return item_data
    
    def track_inventory(self, item_id:int):
        for my_item in self.inventory:
            if my_item["id"] == item_id:
                return my_item
        return None
    
    def update_inventory(self, item_id:int, update_data:Inventory):
        for my_item in self.inventory:
            if my_item["id"] == item_id:
                update_data["stock_value"] = update_data["stock_in_hand"] * update_data["unit_price"]
                my_item.update(update_data)
                return my_item
        return None
    
    def delete_inventory(self, item_id:int):
        for my_item in self.inventory:
            if my_item["id"] == item_id:
                self.inventory.remove(my_item)
                return my_item
        return None
    
    def stock_list(self):
        return self.inventory
