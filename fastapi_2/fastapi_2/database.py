from sqlmodel import Session, create_engine, SQLModel
from supabase import create_client, Client
from .settings import settings

supabase: Client= create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

SUPABASE_URL = settings.SUPABASE_URL

connection_string =str(settings.SUPABASE_DB_URL.replace('postgresql', 'postgresql+psycopg'))

engine = create_engine(connection_string, connect_args={}, pool_recycle=300)

def create_db_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

