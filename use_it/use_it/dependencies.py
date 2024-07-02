from .mock_supabase import MockSupabaseClient
import os, supabase

'''
Now, every time you call get_client, it will return the same 
instance of MockSupabaseClient, and the users list will persist between calls.
'''

client= MockSupabaseClient()
def get_mock_supabase_client():
    return client

def get_supabase_cleint():
    supabase_url= os.getenv("SUPABASE_URL")
    supabase_key= os.getenv("SUPABASE_KEY")
    return supabase.create_client(supabase_url, supabase_key)