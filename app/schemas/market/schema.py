import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, field_validator
from pydantic import UUID4
from pydantic_core.core_schema import FieldValidationInfo


class BidSchema(BaseModel):
    market_session: int
    bid_price: float  # Bid price in BASE unit
    max_payment: float  # Max payment in BASE unit
    resource: str
    gain_func: str

    @field_validator("resource")
    def validate_resource(cls, value):
        if uuid.UUID(value):
            return value
        else:
            raise ValueError("Invalid resource id")

    @field_validator("max_payment")
    def validate_max_payment(cls, value, info: FieldValidationInfo):
        """
        Validate that max_payment is greater than bid_price.
        """
        bid_price = info.data['bid_price']
        if value < bid_price:
            raise ValueError("max_payment must be greater or equal to the bid_price")
        return value

    # @model_validator(mode='before')
    # def convert_max_payment(cls, values):
    #     # Assuming payment_processor is available here as an imported module or object
    #     # Make sure to import or define payment_processor before using it
    #     if 'max_payment' in values:
    #         values['max_payment'] = payment_processor.unit_conversion(
    #             value=float(values['max_payment']),
    #             unit=payment_processor.BASE_UNIT,
    #             target_unit=payment_processor.TRANSACTION_UNIT,
    #             conversion_type=ConversionType.BASE_TO_TRANSACTION
    #         )
    #     return values

    # @model_validator(mode='before')
    # def convert_bid_price(cls, values):
    #     if 'bid_price' in values:
    #         values['bid_price'] = payment_processor.unit_conversion(
    #             value=float(values['bid_price']),
    #             unit=payment_processor.BASE_UNIT,
    #             target_unit=payment_processor.TRANSACTION_UNIT,
    #             conversion_type=ConversionType.BASE_TO_TRANSACTION
    #         )
    #     return values


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


class TransactionSchema(BaseModel):
    transaction_id: str
    timestamp: str
    confirmed: bool
