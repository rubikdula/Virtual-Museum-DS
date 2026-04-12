from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Resolve the database URL.
# On Railway: set DATABASE_URL in the service environment variables,
# pointing at a persistent volume path, e.g.:
#   sqlite:////app/data/virtual_museum.db
# If DATABASE_URL is not set, fall back to a local SQLite file.
if os.getenv("DATABASE_URL"):
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
elif os.getenv("RAILWAY_ENVIRONMENT"):
    # Running on Railway but no explicit DATABASE_URL — use the persistent volume mount.
    data_dir = "/app/data"
    os.makedirs(data_dir, exist_ok=True)
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{data_dir}/virtual_museum.db"
else:
    # Local development
    SQLALCHEMY_DATABASE_URL = "sqlite:///./virtual_museum_v2.db"

print(f"INFO: Using database URL: {SQLALCHEMY_DATABASE_URL}")

# connect_args is only valid for SQLite
_connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=_connect_args)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
