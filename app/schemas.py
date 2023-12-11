import os
from pydantic import BaseModel, Field, EmailStr, field_validator, root_validator
from typing import List
from enum import Enum
import json


class UserWalletSchema(BaseModel):
    email: EmailStr
    password: str  # Be cautious while handling passwords

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "mysecretpassword001!",
            }
        }


class BidSchema(BaseModel):
    email: EmailStr
    price: int
    max_payment: int
    resource: int

    @field_validator("price", "max_payment")
    def check_price_and_max_payment(cls, value):
        if value > 10000000:
            raise ValueError("Price and max payment cannot be greater than 10,000,000")
        return value


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

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "mysecretpassword",
                "password_conf": "mysecretpassword",
                "first_name": "John",
                "last_name": "Doe",
                "role": "user",
                "wallet_address": "some_wallet_address"
            }
        }


class TimeSeriesItem(BaseModel):
    datetime: str = Field(..., example="2020-01-01 00:00:00")
    value: float = Field(..., example=1.0)


class ResourceSchema(BaseModel):
    email: EmailStr
    name: str = Field(..., example="resource-3")
    type: str = Field(..., example="measurements")
    to_forecast: bool = Field(True, example=False)


class MeasurementsSchema(BaseModel):
    email: EmailStr
    resource_name: str = Field(..., example="resource-3")
    time_interval: int = Field(..., example=60)
    aggregation_type: str = Field(..., example="avg")
    units: str = Field(..., example="kw")
    timeseries: List[TimeSeriesItem]

    @field_validator('resource_name')
    def validate_resource_name(cls, resource_name, values):

        user_file_dir = os.environ["USERS_FILE_DIR"]
        with open(os.path.join(user_file_dir, 'users.json'), "r") as f:
            users = json.load(f)

        for user in users:
            if user['email'] == values.data.get('email'):
                valid_resources = [resource['name'] for resource in user['resources']]
                if resource_name in valid_resources:
                    return resource_name
                else:
                    raise ValueError("Invalid resource name.")
        raise ValueError(f"Invalid email.")

    class Config:
        schema_extra = {
            "example": {
                "resource_name": "resource-3",
                "time_interval": 60,
                "aggregation_type": "avg",
                "units": "kw",
                "timeseries": [
                    {"datetime": "2020-01-01 00:00:00", "value": 1.0},
                    {"datetime": "2020-01-01 01:00:00", "value": 2.0},
                ],
            }
        }