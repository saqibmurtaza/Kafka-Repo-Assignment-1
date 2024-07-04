from .mock_order_service import MockOrderService
import os, supabase

# Singleton instance of MockOrderService
mock_order_service= MockOrderService()

def get_mock_order_service():
    return mock_order_service

def get_real_order_service():
    supabase_url=os.getenv("SUPABASE_URL")
    supabase_key=os.getenv("SUPABASE_KEY")
    return supabase.create_client(supabase_key, supabase_url)