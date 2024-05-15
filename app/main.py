import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.dependencies import engine
from app.models.models import User, Token, Base
from app.routes.market import router as market_router
from app.routes.measurements import router as measurements_router
from app.routes.resource import router as resource_router
from app.routes.user import router as user_router
from app.routes.wallet import router as wallet_router

app = FastAPI(
    title="Predico Wallet Client API",
    description="With this API you can register users in the market, send measurements and place bids. "
                "You have a wallet assigned to each user you create using this API This API is part of "
                "the Predico project and its purpose is to allow users to interact with the market while abstracting "
                "the complexity of the underlying technologies",
)

# List of allowed origins (e.g., React app's URL)
origins = [
    "http://localhost:3000",  # Adjust the port if necessary
    "http://192.168.1.164:3000",  # If your React app is also accessible via this address
]

# Add CORSMiddleware to the application instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level:<5} | {message}"
logger.add(os.path.join("files", "logfile.log"), format=log_format, level='DEBUG', backtrace=True)
logger.info("-" * 79)

app.include_router(user_router, prefix="/user", tags=["Authentication"])
app.include_router(resource_router, prefix="/user/resource", tags=["Resource"])
app.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])
app.include_router(market_router, prefix="/market", tags=["Market"])
app.include_router(measurements_router, prefix="/data", tags=["Measurements"])
# Dependency

Base.metadata.create_all(bind=engine)


@app.get("/")
def test() -> dict:
    return {"message": "Welcome to the PREDICO wallet client API. This API is part of the PREDICO project."
                       "With this API you can register users in the market, send measurements and place bids. "
                       "Please refer to the documentation for more information"}
