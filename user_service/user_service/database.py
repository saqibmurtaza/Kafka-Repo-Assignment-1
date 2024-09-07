from sqlmodel import Session, create_engine, SQLModel
from supabase import create_client, Client
from .settings import settings
from .models import MockUser, User

SUPABASE_URL = settings.SUPABASE_URL
supabase: Client= create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

connection_string =str(settings.SUPABASE_DB_URL.
                       replace('postgresql', 'postgresql+psycopg'))
engine = create_engine(connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_tables():
    SQLModel.metadata.create_all(engine, tables=[User.__table__, MockUser.__table__])


