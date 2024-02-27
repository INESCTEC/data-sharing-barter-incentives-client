import ast
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Response, Depends
from payment.PaymentGateway.IOTAPayment.IOTAPaymentController import IOTAPaymentController
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.helpers.helper import wallet_config
from app.schemas.schemas import TransferSchema, WalletSchema, TransferReceiptSchema
from app.apis.RequestStrategy import RequestContext
from app.dependencies import get_request_strategy, get_db_session

from app.helpers.helper import get_header

router = APIRouter()


@router.get("/address")
def get_wallet_address(email: EmailStr):
    wallet_controller = IOTAPaymentController(config=wallet_config())
    try:
        wallet_address = wallet_controller.get_address(email=email)
        wallet_schema = WalletSchema(email=email, address=wallet_address)
    except Exception as e:
        wallet_controller.wallet.destroy()
        error_dict = ast.literal_eval(str(e))
        raise HTTPException(status_code=400, detail=error_dict)

    return Response(content=json.dumps(wallet_schema.model_dump()),
                    status_code=200,
                    media_type="application/json")


@router.get("/transactions")
def get_transactions(email: EmailStr):
    wallet_controller = IOTAPaymentController(config=wallet_config())

    data = []
    try:
        transactions = wallet_controller.get_transaction_history(identifier=email)

        for transaction in transactions:
            ts = datetime.fromtimestamp(int(transaction.timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            data.append({"block_id": transaction.blockId,
                         "timestamp": ts,
                         "transaction_id": transaction.transactionId,
                         "payload": transaction.payload,
                         "inputs": transaction.inputs})

        return Response(content=json.dumps(data),
                        status_code=200,
                        media_type="application/json")

    except Exception as e:
        wallet_controller.wallet.destroy()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/balance")
def balance(email: EmailStr):
    wallet_controller = IOTAPaymentController(config=wallet_config())
    try:
        wallet_balance = wallet_controller.get_balance(identifier=email)
    except Exception as e:
        wallet_controller.wallet.destroy()
        error_dict = ast.literal_eval(str(e))
        raise HTTPException(status_code=400, detail=error_dict)

    return Response(content=json.dumps(wallet_balance), status_code=200, media_type="application/json")


@router.post("/transfer")
def transfer_funds(payload: TransferSchema):
    wallet_controller = IOTAPaymentController(config=wallet_config())
    try:
        response = wallet_controller.execute_transaction(from_identifier=payload.email,
                                                         to_identifier=payload.wallet_address,
                                                         value=payload.amount)

        transfer_receipt_schema = TransferReceiptSchema(transaction_id=response.transactionId,
                                                        payload=response.payload)

        return Response(content=json.dumps(transfer_receipt_schema.model_dump()),
                        status_code=200,
                        media_type="application/json")

    except Exception as e:
        wallet_controller.wallet.destroy()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/request_funds")
def request_funds(email: EmailStr):
    iota_wallet_controller = IOTAPaymentController(config=wallet_config())
    try:
        account = iota_wallet_controller.wallet.get_account(email)
        response = iota_wallet_controller.wallet.get_client().request_funds_from_faucet(
            'https://faucet.testnet.shimmer.network/api/enqueue',
            address=account.addresses()[0].address)
        print(response)
    except Exception as e:
        iota_wallet_controller.wallet.destroy()
        error_dict = ast.literal_eval(str(e))
        raise HTTPException(status_code=400, detail=error_dict)

    return Response(content=response, status_code=200, media_type="application/json")


@router.get("/register")
def register_wallet_address(email: EmailStr,
                            request_strategy: RequestContext = Depends(get_request_strategy)):

    with get_db_session() as db:
        try:
            wallet_controller = IOTAPaymentController(config=wallet_config())
            address = wallet_controller.get_address(email=email)

            header = get_header(db=db)
            response = request_strategy.make_request(endpoint="/user/wallet-address/",
                                                     method="post",
                                                     data={"wallet_address": address},
                                                     headers=header)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")
