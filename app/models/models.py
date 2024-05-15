from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)


class Token(Base):
    """Token model for storing JWT tokens from Predico Server"""
    __tablename__ = "token"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True)  # Ensures each token is stored once
    created_at = Column(DateTime, default=datetime.utcnow)  # Store the time the token was created
    expires_at = Column(DateTime)  # Store the expiration time of the token
