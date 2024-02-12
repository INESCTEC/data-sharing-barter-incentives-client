from app.RequestController import RequestController
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db_session
from app.schemas.schemas import BidSchema
from payment.PaymentGateway.IOTAPayment.IOTAPaymentController import IOTAPaymentController
from app.helpers.helper import wallet_config
from loguru import logger

router = APIRouter()


@router.get("/session")
def session(db: Session = Depends(get_db_session)):
    controller = RequestController(db=db)
    try:
        response = controller.get('api/market/session')
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=response.json(),
                        status_code=200,
                        media_type="application/json")


@router.get("/session/bid/{market_session}")
def session_bid(market_session: int, db: Session = Depends(get_db_session)):

    controller = RequestController(db=db)
    try:
        response = controller.get(f'api/market/bid?market_session={market_session}')
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=response.json(),
                        status_code=200,
                        media_type="application/json")


@router.post("/session/bid")
def session_bid(payload: BidSchema, db: Session = Depends(get_db_session)):
    controller = RequestController(db=db)
    iota_payment = IOTAPaymentController(config=wallet_config())
    try:
        response = controller.get('api/market/wallet-address')

        market_wallet_address = response.json()['data']['wallet_address']

        balance = iota_payment.get_balance(identifier=payload.email)['baseCoin']['available']

        if int(balance) >= payload.max_payment:

            response = controller.post('api/market/bid', json=payload.model_dump())

            # session may not be able for bids
            if response.status_code != 200:
                return JSONResponse(content=response.json(),
                                    status_code=response.status_code,
                                    media_type="application/json")

            bid_id = response.json()['data']['id']

            if response.status_code == 200:

                transaction = iota_payment.execute_transaction(from_identifier=payload.email,
                                                               to_identifier=market_wallet_address,
                                                               value=payload.max_payment)

                data = {"tangle_msg_id": transaction.transactionId}
                response = controller.patch(f'api/market/bid/{bid_id}', json=data)

                return JSONResponse(content=response.json(),
                                    status_code=response.status_code,
                                    media_type="application/json")
            else:
                return JSONResponse(content=response.json(),
                                    status_code=400,
                                    media_type="application/json")
        else:
            return JSONResponse(content={"error": "Insufficient balance"},
                                status_code=400,
                                media_type="application/json")

    except Exception as e:
        logger.error(f"Error executing transaction: {str(e)}")
        iota_payment.wallet.destroy()
        raise HTTPException(status_code=400, detail=str(e))
