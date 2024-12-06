from sqlmodel import Session, create_engine, SQLModel
from supabase import create_client, Client
from .settings import settings
from .models import MockCart, Cart


SUPABASE_URL= settings.SUPABASE_URL
SUPABASE_KEY= settings.SUPABASE_KEY

supabase: Client= create_client(SUPABASE_URL, SUPABASE_KEY)

connection_string= str(settings.SUPABASE_DB_URL.
                       replace('postgresql', 'postgresql+psycopg'))
engine= create_engine(connection_string, connect_args={'sslmode':'require'},
                      pool_recycle=300)

async def get_session():
    with Session(engine) as session:
        yield session

def create_db_tables():
    SQLModel.metadata.create_all(engine, 
                        tables= [Cart.__table__, MockCart.__table__ ])