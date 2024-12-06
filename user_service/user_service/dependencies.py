from fastapi import HTTPException
from .mock_user import MockSupabaseClient
import os, supabase, requests
import logging, httpx


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client_instance= MockSupabaseClient()

def get_mock_supabase_client():
    return client_instance


def get_supabase_cleint():
    supabase_url= os.getenv("SUPABASE_URL")
    supabase_key= os.getenv("SUPABASE_KEY")
    return supabase.create_client(supabase_url, supabase_key)
