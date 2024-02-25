from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.dependencies import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True)  # Ensures each token is stored once
    created_at = Column(DateTime, default=datetime.utcnow)  # Store the time the token was created
    expires_at = Column(DateTime)  # Store the expiration time of the token
