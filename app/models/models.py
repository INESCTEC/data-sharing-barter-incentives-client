from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

    # Relationship with Token
    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")


class Token(Base):
    """Token model for storing JWT tokens from Predico Server"""
    __tablename__ = "token"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)  # Ensures each token is stored once
    created_at = Column(DateTime, default=datetime.utcnow)  # Store the time the token was created
    expires_at = Column(DateTime)  # Store the expiration time of the token

    # Foreign key and relationship with User
    user_email = Column(String, ForeignKey('user.email'), nullable=False)
    user = relationship("User", back_populates="tokens")
