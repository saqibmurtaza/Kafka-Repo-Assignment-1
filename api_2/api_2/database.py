from sqlmodel import Session, create_engine, SQLModel
from api_2 import settings

def creat_db_tables():
    SQLModel.metadata.create_all(engine)

connection_string=str(settings.DATABASE_URL).replace('postgresql', 'postgresql+psycopg')

engine = create_engine(connection_string, connect_args={}, pool_recycle=300)

def get_session():
    with Session(engine) as session:
        yield session

