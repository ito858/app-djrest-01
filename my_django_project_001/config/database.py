from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True for debug, remove in production


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Add a testing-specific session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables when the module is imported
Base.metadata.create_all(engine)
