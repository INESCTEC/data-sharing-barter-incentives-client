from pydantic import BaseModel


class FundResponseModel(BaseModel):
    address: str
    waitingRequests: int


class RegisterWalletResponseDataModel(BaseModel):
    wallet_address: str
    registered_at: str


class RegisterWalletResponseModel(BaseModel):
    code: int
    data: RegisterWalletResponseDataModel
