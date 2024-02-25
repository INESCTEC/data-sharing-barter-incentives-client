import asyncio
import time

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger
from payment.PaymentGateway.IOTAPayment.IOTAPaymentController import IOTAPaymentController
from payment.exceptions.wallet_exceptions import WalletException
from sqlalchemy.orm import Session

from app.apis.RequestStrategy import RequestContext
from app.dependencies import get_db_session, get_request_strategy
from app.helpers.helper import get_header
from app.helpers.helper import wallet_config
from app.schemas.schemas import BidSchema

router = APIRouter()
retries = 3


@router.get("/session")
def session(db: Session = Depends(get_db_session),
            request_strategy: RequestContext = Depends(get_request_strategy)):
    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint="/market/session/",
                                                 method="get",
                                                 headers=header)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=response.json(),
                        status_code=200,
                        media_type="application/json")


@router.get("/session/bid/{market_session}")
def session_bid(market_session: int,
                db: Session = Depends(get_db_session),
                request_strategy: RequestContext = Depends(get_request_strategy)):
    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint=f"/market/bid/?market_session={market_session}",
                                                 method="get",
                                                 headers=header)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=response.json(),
                        status_code=200,
                        media_type="application/json")


@router.post("/session/bid")
async def session_bid(background_tasks: BackgroundTasks,
                      payload: BidSchema,
                      db: Session = Depends(get_db_session),
                      request_strategy: RequestContext = Depends(get_request_strategy)):
    header = get_header(db=db)

    for _ in enumerate(range(retries)):
        try:
            iota_payment = IOTAPaymentController(config=wallet_config())
            break
        except WalletException:
            logger.warning("A wallet error occurred. Retrying...")
            time.sleep(3)
            continue
    else:
        raise HTTPException(status_code=400, detail="Failed to initialize wallet")

    try:
        response = request_strategy.make_request(endpoint="/market/wallet-address/",
                                                 method="get",
                                                 headers=header)

        if response.status_code != 200:
            return JSONResponse(content=response.json(),
                                status_code=response.status_code,
                                media_type="application/json")

        market_wallet_address = response.json()['data']['wallet_address']
        balance = iota_payment.get_balance(identifier=payload.email)['baseCoin']['available']

        if int(balance) >= payload.max_payment:
            response = request_strategy.make_request(endpoint="/market/bid/",
                                                     method="post",
                                                     headers=header,
                                                     json=payload.model_dump())

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
                request_strategy,
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
                                             request_strategy,
                                             bid_id):

    try:
        transaction = await asyncio.to_thread(
            iota_payment.execute_transaction,
            from_identifier=from_identifier,
            to_identifier=to_identifier,
            value=value
        )
        data = {"tangle_msg_id": transaction.transactionId}
        iota_payment.wallet.destroy()
        await asyncio.to_thread(request_strategy.make_request,
                                endpoint=f'api/market/bid/{bid_id}',
                                method='patch',
                                json=data)
    except Exception as e:
        logger.error(f"Error executing transaction: {str(e)}")


def background_task_wrapper(iota_payment,
                            from_identifier,
                            to_identifier,
                            value,
                            request_strategy,
                            bid_id):
    asyncio.run(
        execute_transaction_and_update_bid(iota_payment,
                                           from_identifier,
                                           to_identifier,
                                           value,
                                           request_strategy,
                                           bid_id))
