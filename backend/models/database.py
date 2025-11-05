from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

DATABASE_URL = 'postgresql://postgres.oxyrlxroibooqexazagy:ksvT#w!9DYdd5aH@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'

if not DATABASE_URL:
    raise ValueError("Database url not found")

engine = create_engine(DATABASE_URL)


Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)