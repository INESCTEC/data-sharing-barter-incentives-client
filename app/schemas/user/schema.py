from pydantic import BaseModel, EmailStr
from typing import Optional


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


class UserDetailUpdateModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class RegisterDataModel(BaseModel):
    message: str


class RegisterResponseModel(BaseModel):
    code: int
    data: RegisterDataModel
