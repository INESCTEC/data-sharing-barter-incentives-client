from payment.AbstractPayment import ConversionType
from pydantic import BaseModel
from pydantic import model_validator
from app.dependencies import payment_processor


class FundResponseModel(BaseModel):
    address: str
    waitingRequests: int


class RegisterWalletResponseDataModel(BaseModel):
    wallet_address: str
    registered_at: str


class RegisterWalletResponseModel(BaseModel):
    code: int
    data: RegisterWalletResponseDataModel


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
