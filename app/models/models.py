from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.database import Base
from datetime import datetime, timedelta


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True)  # Ensures each token is stored once
    expires_at = Column(DateTime)  # Store the expiration time of the token

