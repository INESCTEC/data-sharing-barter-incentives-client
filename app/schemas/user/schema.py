from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field, EmailStr, field_validator


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


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str  # Be cautious while handling passwords


class UserSocialLoginSchema(BaseModel):
    token: str
    provider: str


class UserWalletSchema(BaseModel):
    email: EmailStr
    password: str  # Be cautious while handling passwords


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"


class UserRegistrationSchema(BaseModel):
    email: EmailStr
    password: str
    password_conf: str
    first_name: str
    last_name: str
    role: List[str] = Field(..., description="Roles for the user. A user can have multiple roles.")

    @field_validator("role")
    def validate_and_convert_role(cls, role_str):
        role_mapping = {
            "buyer": 1,
            "seller": 2
        }

        for i, role in enumerate(role_str):
            if role not in role_mapping:
                allowed_roles = list(role_mapping.keys())
                raise ValueError(f"Invalid role: {role_str}. Allowed roles are {allowed_roles}")
            role_str[i] = role_mapping[role]
        # We're returning the original string, as you wanted, but can access the integer mapping
        # via the `role_mapping` dictionary elsewhere in the code if needed.
        return role_str

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 9:
            raise ValueError('Password must be at least 9 characters long')

        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain at least one numeric character')

        if not any(char in '!@#$%^&*()_+-=[]{}|:;,.<>?/`~' for char in value):
            raise ValueError('Password must contain at least one special character')

        return value

    @field_validator('role')
    def validate_role(cls, value):
        if not all(isinstance(i, int) for i in value):
            raise ValueError("All roles must be integers.")

        if not all(i in [1, 2] for i in value):
            raise ValueError("Invalid role value. Acceptable values are 1 for Buyer and 2 for Seller.")

        if len(set(value)) != len(value):
            raise ValueError("Roles should be unique. Duplicates are not allowed.")

        return value
