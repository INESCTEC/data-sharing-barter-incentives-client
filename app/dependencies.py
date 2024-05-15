import os
from contextlib import contextmanager

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app.apis.RequestStrategy import RequestContext, RequestsStrategy, DataspaceStrategy
from app.models.models import User

db_username = os.getenv("POSTGRES_USER", "predico")
db_password = os.getenv("POSTGRES_PASSWORD", "predico")
database_host = os.getenv("POSTGRES_HOST", "localhost")
database_name = os.getenv("POSTGRES_DB", "predico")

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_username}:{db_password}@{database_host}/{database_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=20, max_overflow=40, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY")
ALGORITHM = "HS256"


async def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    with get_db_session() as db:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(email: str, password: str, db) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Dependency that provides a session and ensures it is closed after the request
def get_db_session():
    db = SessionLocal()  # Assume SessionLocal is defined elsewhere to provide a Session
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
