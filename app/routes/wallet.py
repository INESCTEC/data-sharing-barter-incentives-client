import ast
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Response
from fastapi import Security
from fastapi.responses import JSONResponse
from payment.AbstractPayment import ConversionType
from payment.PaymentGateway.EthereumPayment.EthereumSmartContract import EthereumSmartContract
from payment.PaymentGateway.IOTAPayment.IOTAPayment import IOTAPaymentController
from payment.database.schemas.generic import (TransactionHistorySchema,
                                              TransactionSchema,
                                              BalanceSchema,
                                              AccountSchema)
from payment.exceptions.wallet_exceptions import WalletException

from app.dependencies import get_current_user
from app.models.models import User
from app.schemas.wallet.schema import TransferSchema, FundResponseModel

from app.dependencies import get_payment_processor

router = APIRouter()

@router.post("/")
def create_wallet(user: User = Security(get_current_user)):
    account = get_payment_processor().create_account(identifier=user.email)
    if account:
        return JSONResponse(content={"message": "Account generated successfully"}, status_code=200)
    return JSONResponse(content={"message": "Account generation failed"}, status_code=400)

@router.get("/validate_transactions",
            response_description="Returns all validated transactions with pending status in the database"
                                 "for the last hour",
            response_model=TransactionHistorySchema)
def get_validate_transfer(user: User = Security(get_current_user)):
    # todo: list all transactions with pending status in the database for the last hour
    payment_processor = get_payment_processor(current_user=user)
    return payment_processor.validate_transactions()


# todo store this information in the database and retrieve it from there
#   make sure an email address has a public address and a private key associated with it
@router.get("/address", response_model=AccountSchema)
def get_wallet_address(user: User = Security(get_current_user)):
    try:
        payment_processor = get_payment_processor(current_user=user)
        return payment_processor.get_account_data(identifier=user.email)
    except Exception as e:
        error_dict = ast.literal_eval(str(e))
        raise HTTPException(status_code=400, detail=error_dict)


@router.post("/filter_transactions_by",
             response_model=TransactionHistorySchema,
             response_description="Get transactions by specific fields and values")
def get_transactions_by(payload: Dict[str, Any],
                        user: User = Security(get_current_user)):
    payment_processor = get_payment_processor(current_user=user)
    return payment_processor.get_transaction_by_field(filters=payload)


@router.get("/transactions", response_model=TransactionHistorySchema)
def get_transactions(user: User = Security(get_current_user)):

    try:
        payment_processor = get_payment_processor(current_user=user)
        if isinstance(payment_processor, IOTAPaymentController):
            identifier = user.email
        else:
            identifier = payment_processor.get_account_data(user.email).address
        return payment_processor.get_transaction_history(identifier=identifier)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/balance", response_model=BalanceSchema)
def get_balance(current_user: User = Security(get_current_user)):

    payment_processor = get_payment_processor(current_user=current_user)
    print(current_user.email)
    try:
        if isinstance(payment_processor, EthereumSmartContract):
            balance = payment_processor.get_balance(
                identifier=payment_processor.get_account_data(current_user.email).address)
        else:
            raise ValueError("Unsupported payment processor type")

        balance.balance = payment_processor.unit_conversion(value=float(balance.balance),
                                                            unit=payment_processor.TRANSACTION_UNIT,
                                                            target_unit=payment_processor.BASE_UNIT,
                                                            conversion_type=ConversionType.TRANSACTION_TO_BASE)
        return balance
    except WalletException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_dict = ast.literal_eval(str(e))
        raise HTTPException(status_code=400, detail=error_dict)


@router.post("/transfer",
             response_description="Transfer funds from one account to another",
             response_model=TransactionSchema)
def post_transfer_funds(payload: TransferSchema, current_user: User = Security(get_current_user)):
    try:
        payment_processor = get_payment_processor(current_user=current_user)
        if isinstance(payment_processor, IOTAPaymentController):
            from_identifier = current_user.email
        else:
            from_identifier = payment_processor.get_account_data(identifier=current_user.email).address

        return payment_processor.execute_transaction(
            from_identifier=from_identifier,
            to_identifier=payload.identifier,
            value=int(payload.amount))

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
