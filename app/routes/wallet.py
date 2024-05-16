import ast
import json
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi import Security
from payment.PaymentGateway.EthereumSmartContract.EthereumSmartContract import EthereumSmartContract
from payment.PaymentGateway.IOTAPayment.IOTAPaymentController import IOTAPaymentController
from payment.schemas.generic import TransactionSchema, BalanceSchema, TransactionHistorySchema, AccountSchema

from app.apis.RequestStrategy import RequestContext
from app.dependencies import get_current_user, get_payment_processor
from app.dependencies import get_request_strategy, get_db_session
from app.helpers.helper import get_header
from app.models.models import User
from app.schemas.schemas import TransferSchema
from app.schemas.wallet.schema import FundResponseModel, RegisterWalletResponseModel

router = APIRouter()


@router.get("/validate_transactions",
            response_description="Returns all validated transactions with pending status in the database"
                                 "for the last hour",
            response_model=TransactionHistorySchema)
def get_validate_transfer(user: User = Security(get_current_user)):
    payment_processor = get_payment_processor()
    return payment_processor.validate_transactions()


# todo store this information in the database and retrieve it from there
#   make sure an email address has a public address and a private key associated with it
@router.get("/address", response_model=AccountSchema)
def get_wallet_address(user: User = Security(get_current_user)):
    try:
        payment_processor = get_payment_processor()
        return payment_processor.get_account_data(identifier=user.email)
    except Exception as e:
        error_dict = ast.literal_eval(str(e))
        raise HTTPException(status_code=400, detail=error_dict)


@router.post("/filter_transactions_by",
             response_model=TransactionHistorySchema,
             response_description="Get transactions by specific fields and values")
def get_transactions_by(payload: Dict[str, Any],
                        user: User = Security(get_current_user)):
    payment_processor = get_payment_processor()
    return payment_processor.get_transaction_by_field(filters=payload)


@router.get("/transactions", response_model=TransactionHistorySchema)
def get_transactions(user: User = Security(get_current_user)):
    payment_processor = get_payment_processor()
    try:
        identifier = payment_processor.get_account_data(user.email).address
        return payment_processor.get_transaction_history(identifier=identifier)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/balance", response_model=BalanceSchema)
def get_balance(current_user: User = Security(get_current_user)):
    try:
        payment_processor = get_payment_processor()
        return payment_processor.get_balance(identifier=current_user.email)
    except Exception as e:
        error_dict = ast.literal_eval(str(e))
        raise HTTPException(status_code=400, detail=error_dict)


@router.post("/transfer",
             response_description="Transfer funds from one account to another",
             response_model=TransactionSchema)
def post_transfer_funds(payload: TransferSchema, current_user: User = Security(get_current_user)):

    payment_processor = get_payment_processor()

    try:
        if isinstance(payment_processor, IOTAPaymentController):
            payload.amount = int(payload.amount)
            from_identifier = current_user.email
        else:
            from_identifier = payment_processor.get_account_data(identifier=current_user.email).address

        return payment_processor.execute_transaction(
            from_identifier=from_identifier,
            to_identifier=payload.identifier,
            value=payload.amount)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/request_funds",
            response_description="Request funds from the faucet - Only available for IOTA",
            response_model=FundResponseModel)
def get_request_funds(user: User = Security(get_current_user)):
    try:
        payment_processor = get_payment_processor()

        if isinstance(payment_processor, EthereumSmartContract):
            raise HTTPException(status_code=400, detail="Faucet not available for Ethereum")

        address = payment_processor.get_account_data(identifier=user.email).address
        response = payment_processor.request_funds(identifier=address)
    except Exception as e:
        error_dict = ast.literal_eval(str(e))
        raise HTTPException(status_code=400, detail=error_dict)

    return Response(content=response, status_code=200, media_type="application/json")


@router.get("/register",
            response_description="Register a new account and initialize the wallet",
            response_model=RegisterWalletResponseModel)
def get_register_wallet_address(request_strategy: RequestContext = Depends(get_request_strategy),
                                db=Depends(get_db_session),
                                user: User = Security(get_current_user)):
    payment_processor = get_payment_processor()

    try:
        payment_processor.initialize_payment_method()
        address = payment_processor.get_account_data(identifier=user.email).address

        header = get_header(db=db)
        response = request_strategy.make_request(endpoint="/user/wallet-address/",
                                                 method="post",
                                                 data={"wallet_address": address},
                                                 headers=header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")
