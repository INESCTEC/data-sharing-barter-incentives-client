from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class MarketWalletResponseDataModel(BaseModel):
    wallet_address: str
    registered_at: str


class UserWalletResponseDataModel(BaseModel):
    user_id: UUID
    wallet_address: str
    registered_at: str


class MarketWalletResponseModel(BaseModel):
    code: int
    data: MarketWalletResponseDataModel


class UserMarketWalletResponseModel(BaseModel):
    code: int
    data: UserWalletResponseDataModel


class MarketSessionData(BaseModel):
    id: int
    session_number: int
    session_date: str
    staged_ts: datetime
    open_ts: datetime
    close_ts: Optional[datetime]
    launch_ts: Optional[datetime]
    finish_ts: Optional[datetime]
    status: str
    market_price: float
    b_min: float
    b_max: float
    n_price_steps: int
    delta: float


class MarketSessionsResponse(BaseModel):
    data: list[MarketSessionData]


class UserMarketWalletPayload(BaseModel):
    wallet_address: str
