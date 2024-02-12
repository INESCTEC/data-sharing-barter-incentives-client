import os

from fastapi import FastAPI
from loguru import logger
from app.database import engine
from app.models import models

from app.routers.measurements import router as measurements_router
from app.routers.resource import router as resource_router
from app.routers.forecast import router as forecast_router
from app.routers.market import router as market_router
from app.routers.user import router as user_router
from app.routers.wallet import router as wallet_router

app = FastAPI(
    title="Predico Wallet Client API",
    description="With this API you can register users in the market, send measurements and place bids. "
                "You have a wallet assigned to each user you create using this API This API is part of "
                "the Predico project and its purpose is to allow users to interact with the market while abstracting "
                "the complexity of the underlying technologies",
)

log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level:<5} | {message}"
logger.add(os.path.join("files", "logfile.log"), format=log_format, level='DEBUG', backtrace=True)
logger.info("-" * 79)

app.include_router(user_router, prefix="/user", tags=["Authentication"])
app.include_router(resource_router, prefix="/user/resource", tags=["Resource"])
app.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])
app.include_router(market_router, prefix="/market", tags=["Market"])
app.include_router(forecast_router, prefix="/user/forecast", tags=["Forecast"])
app.include_router(measurements_router, prefix="/user/data", tags=["Data"])
# Dependency

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def test() -> dict:
    return {"message": "Welcome to the PREDICO wallet client API. This API is part of the PREDICO project."
                       "With this API you can register users in the market, send measurements and place bids. "
                       "Please refer to the documentation for more information"}






