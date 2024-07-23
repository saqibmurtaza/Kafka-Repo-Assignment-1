from .mock_inv_service import MockInventoryService
import supabase, os

inventory_service_instance= MockInventoryService()

def get_mock_inventory():
    return inventory_service_instance

def get_real_inventory():
    supabase_url= os.getenv("SUPABASE_URL")
    supabase_key= os.getenv("SUPABASE_KEY")
    return supabase.create_client(supabase_key, supabase_url)