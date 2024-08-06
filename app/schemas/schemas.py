import uuid
from enum import Enum
from typing import List

from payment.AbstractPayment import ConversionType
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator

from app.dependencies import payment_processor


class TransactionSchema(BaseModel):
    # Define the fields of your Transaction object here
    # This is an example; adjust it according to your actual Transaction object structure
    type: int
    essence: dict
    unlocks: List[dict]
    inclusionState: str
    timestamp: str
    transactionId: str
    networkId: str
    incoming: bool
    note: str
    blockId: str


class TransferReceiptSchema(BaseModel):
    transaction_id: str
    payload: dict


class WalletSchema(BaseModel):
    email: EmailStr
    address: str


class TransferSchema(BaseModel):
    amount: int  # amount in BASE unit
    identifier: str  # The email address or public address of the recipient

    @model_validator(mode='before')
    def convert_amount(cls, values):
        if 'amount' in values:
            values['amount'] = int(payment_processor.unit_conversion(
                value=float(values['amount']),
                unit=payment_processor.BASE_UNIT,
                target_unit=payment_processor.TRANSACTION_UNIT,
                conversion_type=ConversionType.BASE_TO_TRANSACTION
            ))
        return values


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str  # Be cautious while handling passwords


class UserWalletSchema(BaseModel):
    email: EmailStr
    password: str  # Be cautious while handling passwords


class BidSchema(BaseModel):
    market_session: int
    bid_price: int  # Bid price in BASE unit
    max_payment: int  # Max payment in BASE unit
    resource: str
    gain_func: str

    @field_validator("resource")
    def validate_resource(cls, value):
        if uuid.UUID(value):
            return value
        else:
            raise ValueError("Invalid resource id")

    @field_validator("max_payment")
    def validate_max_payment(cls, value, values):
        """
        Validate that max_payment is greater than bid_price.
        """
        bid_price = values.get('bid_price')
        if bid_price is not None and value <= bid_price:
            raise ValueError("max_payment must be greater than bid_price")
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


class TimeSeriesItem(BaseModel):
    datetime: str = Field(..., example="2020-01-01 00:00:00")
    value: float = Field(..., example=1.0)


class MeasurementsSchema(BaseModel):
    resource_name: str = Field(..., example="resource-3")
    time_interval: int = Field(..., example=60)
    aggregation_type: str = Field(..., example="avg")
    units: str = Field(..., example="kw")
    timeseries: List[TimeSeriesItem]

    # @field_validator('resource_name')
    # def validate_resource_name(cls, resource_name, values):
    #
    #     user_file_dir = os.environ["USERS_FILE_DIR"]
    #     with open(os.path.join(user_file_dir, 'users.json'), "r") as f:
    #         users = json.load(f)
    #
    #     for user in users:
    #         if user['email'] == values.data.get('email'):
    #             valid_resources = [resource['name'] for resource in user['resources']]
    #             if resource_name in valid_resources:
    #                 return resource_name
    #             else:
    #                 raise ValueError("Invalid resource name.")
    #     raise ValueError(f"Invalid email.")
