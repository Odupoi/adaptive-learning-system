from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
#from app.config import DATABASE_URL
from app.config import get_settings

settings = get_settings()

DATABASE_URL = settings.database_url

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True  # recommended for modern SQLAlchemy
)

# Session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)