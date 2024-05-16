from app.models.models import Token
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timedelta


def add_token(db: Session, token: str, expires_in=3600) -> Token:
    expiration_time = datetime.utcnow() + timedelta(seconds=expires_in)
    new_token = Token(token=token, expires_at=expiration_time)
    db.add(new_token)
    db.commit()
    db.close()
    return new_token


def get_token(db: Session) -> Optional[Token]:

    current_time = datetime.utcnow()
    # Query for tokens where the expiration time is greater than the current time
    # noinspection PyTypeChecker
    query = db.query(Token).filter(Token.expires_at > current_time).order_by(
        desc(Token.created_at)).first()

    return query


async def cleanup_expired_tokens(db: Session):
    # Calculate the current time
    current_time = datetime.utcnow()
    # Delete expired tokens from the Token table
    # noinspection PyTypeChecker
    db.query(Token).filter(Token.expires_at < current_time).delete()
    # Commit the changes
    db.commit()
