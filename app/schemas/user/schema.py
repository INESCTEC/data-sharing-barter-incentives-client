from pydantic import BaseModel


class LoginResponseModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserDetailResponseModel(BaseModel):
    fist_name: str
    last_name: str
    email: str
    date_joined: str
    last_login: str


class RegisterDataModel(BaseModel):
    message: str


class RegisterResponseModel(BaseModel):
    code: int
    data: RegisterDataModel
