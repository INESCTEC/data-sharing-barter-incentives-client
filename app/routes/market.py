import asyncio
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger
from payment.PaymentGateway.IOTAPayment.IOTAPaymentController import IOTAPaymentController
from payment.exceptions.wallet_exceptions import WalletException

from app.apis.RequestStrategy import RequestContext
from app.dependencies import get_db_session, get_request_strategy, get_current_user, get_payment_processor
from app.helpers.helper import get_header
from app.schemas.market.schema import (MarketWalletResponseModel,
                                       UserMarketWalletResponseModel,
                                       MarketSessionsResponse,
                                       MarketSessionStatus)
from app.schemas.schemas import BidSchema

router = APIRouter()
retries = 3


def make_market_request(endpoint: str, request_strategy: RequestContext, db_session):
    try:
        header = get_header(db=db_session)
        response = request_strategy.make_request(endpoint=endpoint, method="get", headers=header)
        return JSONResponse(content=response.json(), status_code=200, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wallet/user_wallet_address",
            response_description="Get the user wallet address registered in the market",
            response_model=UserMarketWalletResponseModel)
def get_user_address(request_strategy: RequestContext = Depends(get_request_strategy),
                     db=Depends(get_db_session)):
    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint="/user/wallet-address/",
                                                 method="get",
                                                 headers=header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=response.json(),
                        status_code=200,
                        media_type="application/json")


@router.post("/wallet/user_wallet_address",
             response_description="Register the user wallet address in the market",
             response_model=UserMarketWalletResponseModel)
def post_user_address(request_strategy: RequestContext = Depends(get_request_strategy),
                      user=Depends(get_current_user),
                      db=Depends(get_db_session)):
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

    return JSONResponse(content=response.json(),
                        status_code=200,
                        media_type="application/json")


@router.get("/wallet/market_wallet_address",
            response_description="Get the market wallet address registered in the market",
            response_model=MarketWalletResponseModel)
def get_market_address(request_strategy: RequestContext = Depends(get_request_strategy),
                       db=Depends(get_db_session)):
    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint="/market/wallet-address/",
                                                 method="get",
                                                 headers=header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=response.json(),
                        status_code=200,
                        media_type="application/json")


@router.get("/session", response_model=MarketSessionsResponse)
def get_session(status: Optional[MarketSessionStatus] = "open",
                request_strategy: RequestContext = Depends(get_request_strategy),
                db=Depends(get_db_session)):
    try:
        endpoint = "/market/session/"
        if status:
            endpoint += f"?market_session_status={status}"
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint=endpoint,
                                                 method="get",
                                                 headers=header)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=response.json(),
                        status_code=200,
                        media_type="application/json")


@router.get("/session/balance")
def get_session_balance(by_resource: Optional[bool] = True,
                        request_strategy: RequestContext = Depends(get_request_strategy),
                        db=Depends(get_db_session)):
    endpoint = f"/market/session-balance/?balance_by_resource={by_resource}"
    return make_market_request(endpoint=endpoint,
                               request_strategy=request_strategy,
                               db_session=db)


@router.get("/session/bid/{market_session}")
def get_session_bid(market_session: int,
                    request_strategy: RequestContext = Depends(get_request_strategy),
                    db=Depends(get_db_session)):
    endpoint = f"/market/bid/?market_session={market_session}"
    return make_market_request(endpoint=endpoint,
                               request_strategy=request_strategy,
                               db_session=db)


@router.post("/session/bid")
async def get_session_bid(background_tasks: BackgroundTasks,
                          payload: BidSchema,
                          request_strategy: RequestContext = Depends(get_request_strategy),
                          user=Depends(get_current_user),
                          db=Depends(get_db_session)):
    header = get_header(db=db)

    for _ in enumerate(range(retries)):
        try:
            payment_processor = get_payment_processor()
            payment_processor.initialize_payment_method()
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

        # Check if user has sufficient balance particular parameter to IOTA
        # todo fix this to be more generic
        if isinstance(payment_processor, IOTAPaymentController):
            balance = payment_processor.get_balance(identifier=user.email).balance
            user_address = user.email
        else:
            balance = payment_processor.get_balance().balance
            user_address = payment_processor.get_account_data(identifier=user.email).address

        if int(balance) >= payload.max_payment:
            response = request_strategy.make_request(endpoint="/market/bid/",
                                                     method="post",
                                                     headers=header,
                                                     data=payload.model_dump())

            if response.status_code != 200:
                return JSONResponse(content=response.json(),
                                    status_code=response.status_code,
                                    media_type="application/json")

            bid_id = response.json()['data']['id']

            # Add background task for transaction execution and bid update
            background_tasks.add_task(
                background_task_wrapper,
                payment_processor,
                user_address,
                market_wallet_address,
                payload.max_payment,
                request_strategy,
                bid_id,
                header
            )

            return JSONResponse(content={"message": "Bid successfully posted. "
                                                    "Transaction in progress..."},
                                status_code=202,
                                media_type="application/json")
        else:
            return JSONResponse(content={"error": "Insufficient balance"},
                                status_code=400,
                                media_type="application/json")

    except Exception as e:
        logger.error(f"Error while posting bid: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


async def execute_transaction_and_update_bid(payment_processor,
                                             from_identifier,
                                             to_identifier,
                                             value,
                                             request_strategy,
                                             bid_id,
                                             header):
    try:
        transaction = await asyncio.to_thread(
            payment_processor.execute_transaction,
            from_identifier=from_identifier,
            to_identifier=to_identifier,
            value=value
        )
        data = {"tangle_msg_id": transaction.tx_receipt}

        await asyncio.to_thread(request_strategy.make_request,
                                endpoint=f'/market/bid/{bid_id}',
                                method='patch',
                                data=data,
                                headers=header)
    except Exception as e:
        logger.error(f"Error executing transaction: {str(e)}")


def background_task_wrapper(payment_processor,
                            from_identifier,
                            to_identifier,
                            value,
                            request_strategy,
                            bid_id,
                            header):
    asyncio.run(
        execute_transaction_and_update_bid(payment_processor,
                                           from_identifier,
                                           to_identifier,
                                           value,
                                           request_strategy,
                                           bid_id,
                                           header))


@router.get("/session/transactions")
def session_transactions(request_strategy: RequestContext = Depends(get_request_strategy),
                         db=Depends(get_db_session)):
    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint="/market/session-transactions/",
                                                 method="get",
                                                 headers=header)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=response.json(),
                        status_code=200,
                        media_type="application/json")
