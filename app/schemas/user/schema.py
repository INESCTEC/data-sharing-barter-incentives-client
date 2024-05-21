from pydantic import BaseModel


class LoginResponseModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RegisterDataModel(BaseModel):
    message: str


class RegisterResponseModel(BaseModel):
    code: int
    data: RegisterDataModel
