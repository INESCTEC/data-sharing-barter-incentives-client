import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from contextlib import contextmanager
from app.apis.RequestStrategy import RequestContext, RequestsStrategy, DataspaceStrategy

db_username = os.getenv("DB_USERNAME", "predico")
db_password = os.getenv("DB_PASSWORD", "predico")
database_host = os.getenv("DB_HOST", "192.168.1.164")
database_name = os.getenv("DB_NAME", "predico")

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_username}:{db_password}@{database_host}/{database_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=20, max_overflow=40, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_request_strategy() -> RequestContext:
    # Example: Decide which strategy to use based on an environment variable
    use_dataspace_connector = os.getenv("USE_DATASPACE", "false").lower() == "true"

    if use_dataspace_connector:
        strategy = DataspaceStrategy()
    else:
        strategy = RequestsStrategy()

    return RequestContext(strategy)
