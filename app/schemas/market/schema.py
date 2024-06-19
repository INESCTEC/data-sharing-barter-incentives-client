from pydantic import BaseModel, UUID4
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from enum import Enum


class MarketSessionStatus(str, Enum):
    finished = "finished"
    open = "open"
    closed = "closed"
    running = "running"


class UserBalanceDetailSchema(BaseModel):
    user: UUID4
    balance: float
    total_deposit: float
    total_withdraw: float
    total_payment: float
    total_revenue: float
    updated_at: datetime


class SessionData(BaseModel):
    market_session: int
    user: UUID
    resource: UUID
    session_deposit: float
    session_balance: float
    session_payment: float
    session_revenue: float
    registered_at: datetime


class UserMarketBalanceSessionResponseSchema(BaseModel):
    code: int
    data: List[SessionData]


class UserMarketBalanceResponseSchema(BaseModel):
    code: int
    data: List[UserBalanceDetailSchema]


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
