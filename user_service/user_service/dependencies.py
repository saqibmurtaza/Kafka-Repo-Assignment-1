import os

def get_supabase_client():
    if os.getenv("USE_MOCK_SUPABASE", "false").lower() == "true":
        from .mock_supabase import get_mock_supabase_client
        return get_mock_supabase_client()
    else:
        import supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        return supabase.create_client(supabase_url, supabase_key)
