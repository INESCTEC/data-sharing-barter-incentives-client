import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from payment.AbstractPayment import AbstractPayment
from payment.database.PaymentDatabase import PaymentDatabase as BlockchainDatabase
from payment.PaymentGateway.EthereumSmartContract.EthereumSmartContract import (EthereumSmartContract,
                                                                                ethereum_provider)
from payment.PaymentGateway.IOTAPayment.IOTAPaymentController import IOTAPaymentController

from payment.database.schemas.ethereum_schema import EthereumAccountSchema
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from app.apis.RequestStrategy import RequestContext, RequestsStrategy, DataspaceStrategy
from app.helpers.helper import wallet_config, smart_contract_config
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
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
ALGORITHM = "HS256"


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(email: str, password: str, db: Session) -> User:
    # noinspection PyTypeChecker
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return user


def get_payload_from_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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


def get_payment_processor() -> AbstractPayment:

    blockchain_db = BlockchainDatabase(engine)
    payment_type = os.getenv("PAYMENT_PROCESSOR_TYPE", "IOTA")  # Default to IOTA if not specified

    try:
        if payment_type == "IOTA":
            payment_controller = IOTAPaymentController(config=wallet_config(), payment_db=blockchain_db)
            payment_controller.initialize_payment_method()
            return payment_controller

        elif payment_type == "ERC20":
            config = smart_contract_config()
            provider_url = os.getenv('WEB3_PROVIDER_URL')
            if not provider_url:
                raise ValueError("WEB3_PROVIDER_URL environment variable not set")
            w3 = ethereum_provider(url=provider_url)
            eth_public_key = os.getenv('ETH_PUBLIC_KEY')
            eth_private_key = os.getenv('ETH_PRIVATE_KEY')

            if eth_public_key and eth_private_key:
                account = EthereumAccountSchema(
                    public_address=eth_public_key,
                    private_key=eth_private_key)

                return EthereumSmartContract(config=config,
                                             account=account,
                                             payment_db=blockchain_db,
                                             web3_instance=w3)

            return EthereumSmartContract(config=config,
                                         payment_db=blockchain_db,
                                         web3_instance=w3)

        elif payment_type == "FIAT":
            raise NotImplementedError("Fiat payment processor not yet supported")
        else:
            raise ValueError("Unsupported payment processor type")
    except Exception as e:
        raise e


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: Session = Depends(get_db_session)):

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

    # noinspection PyTypeChecker
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def get_request_strategy() -> RequestContext:
    # Example: Decide which strategy to use based on an environment variable
    use_dataspace_connector = os.getenv("USE_DATASPACE", "false").lower() == "true"

    if use_dataspace_connector:
        strategy = DataspaceStrategy()
    else:
        strategy = RequestsStrategy()

    return RequestContext(strategy)


payment_processor = get_payment_processor()
