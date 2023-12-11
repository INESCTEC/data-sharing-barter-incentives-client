import os
from fastapi import FastAPI
from loguru import logger
from app.routers.resource import router as resource_router
from app.routers.session import router as session_router
from app.routers.user import router as user_router
from app.routers.wallet import router as wallet_router
from app.routers.measurements import router as measurements_router

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

app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(resource_router, prefix="/resource", tags=["resource"])
app.include_router(wallet_router, prefix="/wallet", tags=["wallet"])
app.include_router(session_router, prefix="/session", tags=["session"])
app.include_router(measurements_router, prefix="/data", tags=["data"])


@app.get("/")
def test() -> dict:
    return {"message": "Welcome to the PREDICO wallet client API. This API is part of the PREDICO project."
                       "With this API you can register users in the market, send measurements and place bids. "
                       "Please refer to the documentation for more information"}






