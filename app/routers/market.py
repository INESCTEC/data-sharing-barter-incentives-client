import asyncio

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger
from payment.PaymentGateway.IOTAPayment.IOTAPaymentController import IOTAPaymentController
from sqlalchemy.orm import Session

from app.RequestController import RequestController
from app.database import get_db_session
from app.helpers.helper import wallet_config
from app.schemas.schemas import BidSchema

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
async def session_bid(background_tasks: BackgroundTasks,
                      payload: BidSchema,
                      db: Session = Depends(get_db_session)):
    controller = RequestController(db=db)
    iota_payment = IOTAPaymentController(config=wallet_config())

    try:
        response = controller.get('api/market/wallet-address')
        market_wallet_address = response.json()['data']['wallet_address']
        balance = iota_payment.get_balance(identifier=payload.email)['baseCoin']['available']

        if int(balance) >= payload.max_payment:
            response = controller.post('api/market/bid', json=payload.model_dump())

            if response.status_code != 200:
                return JSONResponse(content=response.json(),
                                    status_code=response.status_code,
                                    media_type="application/json")

            bid_id = response.json()['data']['id']

            # Add background task for transaction execution and bid update
            background_tasks.add_task(
                background_task_wrapper,
                iota_payment,
                payload.email,
                market_wallet_address,
                payload.max_payment,
                controller,
                bid_id
            )

            return JSONResponse(content={"message": "Bid successfully posted. Transaction in progress..."},
                                status_code=202,
                                media_type="application/json")
        else:
            return JSONResponse(content={"error": "Insufficient balance"},
                                status_code=400,
                                media_type="application/json")

    except Exception as e:
        logger.error(f"Error while posting bid: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


async def execute_transaction_and_update_bid(iota_payment,
                                             from_identifier,
                                             to_identifier,
                                             value,
                                             controller,
                                             bid_id):
    transaction = await asyncio.to_thread(
        iota_payment.execute_transaction,
        from_identifier=from_identifier,
        to_identifier=to_identifier,
        value=value
    )
    data = {"tangle_msg_id": transaction.transactionId}
    await asyncio.to_thread(controller.patch, f'api/market/bid/{bid_id}', json=data)


def background_task_wrapper(iota_payment,
                            from_identifier,
                            to_identifier,
                            value,
                            controller,
                            bid_id):
    asyncio.run(
        execute_transaction_and_update_bid(iota_payment,
                                           from_identifier,
                                           to_identifier,
                                           value,
                                           controller,
                                           bid_id))
