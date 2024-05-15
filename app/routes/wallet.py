import ast
import json
import os

from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi import Security
from payment.AbstractPayment import AbstractPayment
from payment.PaymentGateway.BlockchainDatabase import BlockchainDatabase
from payment.PaymentGateway.EthereumSmartContract.EthereumSmartContract import EthereumSmartContract
from payment.PaymentGateway.IOTAPayment.IOTAPaymentController import IOTAPaymentController
from payment.schemas.ethereum_schema import EthereumAccountSchema
from payment.schemas.generic import TransactionSchema, BalanceSchema, TransactionHistorySchema
from pydantic import EmailStr

from app.apis.RequestStrategy import RequestContext
from app.dependencies import get_current_user
from app.dependencies import get_request_strategy, get_db_session, engine
from app.helpers.helper import get_header
from app.helpers.helper import wallet_config, smart_contract_config
from app.models.models import User
from app.schemas.schemas import TransferSchema, WalletSchema

router = APIRouter()


def get_payment_processor() -> AbstractPayment:
    payment_type = os.getenv("PAYMENT_PROCESSOR_TYPE", "IOTA")  # Default to IOTA if not specified
    if payment_type == "IOTA":
        return IOTAPaymentController(config=wallet_config())
    elif payment_type == "ERC20":
        account = EthereumAccountSchema(
            public_address='0x9AD9Ff0C9b1c5437548e350DD95526354e57b323',
            private_key='03dfd0949c4798da957a811bbb07a56afea6706513f6b5f1b35759e0c1ade29e')
        blockchain_db = BlockchainDatabase(engine)
        config = smart_contract_config()
        return EthereumSmartContract(config=config, account=account, blockchain_db=blockchain_db)
    else:
        raise ValueError("Unsupported payment processor type")


# todo store this information in the database and retrieve it from there
#   make sure an email address has a public address and a private key associated with it
@router.get("/address")
def get_wallet_address(email: EmailStr):
    payment_processor = get_payment_processor()
    try:
        account_data = payment_processor.get_account_data(identifier=email)
        wallet_schema = WalletSchema(email=email, address=account_data.address)
    except Exception as e:
        error_dict = ast.literal_eval(str(e))
        raise HTTPException(status_code=400, detail=error_dict)

    return Response(content=json.dumps(wallet_schema.model_dump()),
                    status_code=200,
                    media_type="application/json")


# todo store this information in the database and retrieve it from there
#   we are only interested in the transactions that are associated with the email address
@router.get("/transactions", response_model=TransactionHistorySchema)
def get_transactions(user: User = Security(get_current_user)):
    payment_processor = get_payment_processor()
    try:
        address = payment_processor.get_account_data(user.email).address
        return payment_processor.get_transaction_history(identifier=address)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/balance", response_model=BalanceSchema)
def balance(current_user: User = Security(get_current_user)):
    payment_processor = get_payment_processor()
    try:
        return payment_processor.get_balance()
    except Exception as e:
        error_dict = ast.literal_eval(str(e))
        raise HTTPException(status_code=400, detail=error_dict)


@router.post("/transfer",
             response_description="Transfer funds from one account to another",
             response_model=TransactionSchema)
def transfer_funds(payload: TransferSchema, current_user: User = Security(get_current_user)):
    payment_processor = get_payment_processor()

    try:
        if isinstance(payment_processor, IOTAPaymentController):
            payload.amount = int(payload.amount)
        return payment_processor.execute_transaction(
            from_identifier=payment_processor.get_account_data(identifier=current_user.email).address,
            to_identifier=payload.identifier,
            value=payload.amount)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/request_funds",
            response_description="Request funds from the faucet")
def request_funds(email: EmailStr):
    payment_processor = get_payment_processor()
    if isinstance(payment_processor, EthereumSmartContract):
        raise HTTPException(status_code=400, detail="Faucet not available for Ethereum")

    try:
        address = payment_processor.get_account_data(identifier=email).address
        response = payment_processor.request_funds(identifier=address)
    except Exception as e:
        error_dict = ast.literal_eval(str(e))
        raise HTTPException(status_code=400, detail=error_dict)

    return Response(content=response, status_code=200, media_type="application/json")


@router.get("/register",
            response_description="Register a new account and initialize the wallet")
def register_wallet_address(email: EmailStr,
                            request_strategy: RequestContext = Depends(get_request_strategy)):
    payment_processor = get_payment_processor()

    with get_db_session() as db:
        try:
            payment_processor.initialize_payment_method()
            address = payment_processor.get_account_data(identifier=email).address

            header = get_header(db=db)
            response = request_strategy.make_request(endpoint="/user/wallet-address/",
                                                     method="post",
                                                     data={"wallet_address": address},
                                                     headers=header)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")
