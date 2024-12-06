from supabase import Client
from typing import Union
from .mock_order import MockOrderService
from .settings import settings
import os, supabase, logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

# Singleton instance of MockOrderService
mock_order_instance = MockOrderService()

def get_mock_order_service():  
    return mock_order_instance

def get_real_order_service():
    supabase_url=os.getenv("SUPABASE_URL")
    supabase_key=os.getenv("SUPABASE_KEY")
    return supabase.create_client(supabase_key, supabase_url)

