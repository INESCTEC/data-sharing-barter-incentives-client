import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status as http_status
from fastapi.responses import JSONResponse
from loguru import logger
from payment.PaymentGateway.IOTAPayment.IOTAPayment import IOTAPaymentController

from app.apis.RequestStrategy import RequestContext
from app.dependencies import get_db_session, get_request_strategy, get_current_user, payment_processor
from app.helpers.helper import get_header
from app.models.models import User
from app.schemas.market.schema import (MarketWalletResponseModel,
                                       UserMarketWalletResponseModel,
                                       MarketSessionsResponse,
                                       MarketSessionStatus,
                                       UserMarketBalanceSessionResponseSchema,
                                       UserMarketBalanceResponseSchema)
from app.schemas.schemas import BidSchema

router = APIRouter()
retries = 3


def make_market_request(endpoint: str, request_strategy: RequestContext, db_session, user_email: str):
    try:
        header = get_header(db=db_session, user_email=user_email)
        response = request_strategy.make_request(endpoint=endpoint, method="get", headers=header)
        return JSONResponse(content=response.json(), status_code=response.status_code, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wallet/user_wallet_address",
            response_description="Get the user wallet address registered in the market",
            response_model=UserMarketWalletResponseModel)
def get_user_address(request_strategy: RequestContext = Depends(get_request_strategy),
                     user=Depends(get_current_user),
                     db=Depends(get_db_session)):
    try:
        header = get_header(db=db, user_email=user.email)
        response = request_strategy.make_request(endpoint="/user/wallet-address/",
                                                 method="get",
                                                 headers=header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=response.json(),
                        status_code=response.status_code,
                        media_type="application/json")


@router.post("/wallet/user_wallet_address",
             response_description="Register the user wallet address in the market",
             response_model=UserMarketWalletResponseModel)
def post_user_address(request_strategy: RequestContext = Depends(get_request_strategy),
                      user=Depends(get_current_user),
                      db=Depends(get_db_session)):
    try:
        payment_processor.initialize_payment_method()
        address = payment_processor.get_account_data(identifier=user.email).address
        header = get_header(db=db, user_email=user.email)
        response = request_strategy.make_request(endpoint="/user/wallet-address/",
                                                 method="post",
                                                 data={"wallet_address": address},
                                                 headers=header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=response.json(),
                        status_code=response.status_code,
                        media_type="application/json")


@router.get("/wallet/market_wallet_address",
            response_description="Get the market wallet address registered in the market",
            response_model=MarketWalletResponseModel)
def get_market_address(request_strategy: RequestContext = Depends(get_request_strategy),
                       user=Depends(get_current_user),
                       db=Depends(get_db_session)):
    try:
        header = get_header(db=db, user_email=user.email)
        response = request_strategy.make_request(endpoint="/market/wallet-address/",
                                                 method="get",
                                                 headers=header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=response.json(),
                        status_code=response.status_code,
                        media_type="application/json")


@router.get("/unit")
def get_unit(user=Depends(get_current_user)):

    response_content = {
        "base_unit": payment_processor.BASE_UNIT,
        "transaction_unit": payment_processor.TRANSACTION_UNIT,
        "rates": payment_processor.CONVERSION_RATES
    }

    return JSONResponse(content=response_content,
                        status_code=http_status.HTTP_200_OK,
                        media_type="application/json")


@router.get("/session", response_model=MarketSessionsResponse)
def get_session(status: Optional[MarketSessionStatus] = "open",
                request_strategy: RequestContext = Depends(get_request_strategy),
                user=Depends(get_current_user),
                db=Depends(get_db_session)):
    try:
        endpoint = "/market/session/"
        if status:
            endpoint += f"?market_session_status={status}"
        header = get_header(db=db, user_email=user.email)
        response = request_strategy.make_request(endpoint=endpoint,
                                                 method="get",
                                                 headers=header)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=response.json(),
                        status_code=response.status_code,
                        media_type="application/json")


@router.get("/session/balance", response_model=UserMarketBalanceSessionResponseSchema)
def get_session_balance(by_resource: Optional[bool] = False,
                        request_strategy: RequestContext = Depends(get_request_strategy),
                        user: User = Depends(get_current_user),
                        db=Depends(get_db_session)):
    endpoint = f"/market/session-balance/?balance_by_resource={by_resource}"
    return make_market_request(endpoint=endpoint,
                               request_strategy=request_strategy,
                               db_session=db,
                               user_email=user.email)


@router.get("/balance", response_model=UserMarketBalanceResponseSchema)
def get_balance(request_strategy: RequestContext = Depends(get_request_strategy),
                user: User = Depends(get_current_user),
                db=Depends(get_db_session)):
    return make_market_request(endpoint="/market/balance",
                               request_strategy=request_strategy,
                               db_session=db,
                               user_email=user.email)


@router.get("/session/bid/{market_session}")
def get_session_bid(market_session: int,
                    request_strategy: RequestContext = Depends(get_request_strategy),
                    user: User = Depends(get_current_user),
                    db=Depends(get_db_session)):
    endpoint = f"/market/bid/?market_session={market_session}"
    return make_market_request(endpoint=endpoint,
                               request_strategy=request_strategy,
                               db_session=db,
                               user_email=user.email)


@router.post("/session/bid")
async def get_session_bid(background_tasks: BackgroundTasks,
                          payload: BidSchema,
                          request_strategy: RequestContext = Depends(get_request_strategy),
                          user=Depends(get_current_user),
                          db=Depends(get_db_session)):

    header = get_header(db=db, user_email=user.email)

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


async def execute_transaction_and_update_bid(from_identifier,
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
        data = {"transaction_id": transaction.receipt}

        await asyncio.to_thread(request_strategy.make_request,
                                endpoint=f'/market/bid/{bid_id}',
                                method='patch',
                                data=data,
                                headers=header)
    except Exception as e:
        logger.error(f"Error executing transaction: {str(e)}")


def background_task_wrapper(from_identifier,
                            to_identifier,
                            value,
                            request_strategy,
                            bid_id,
                            header):
    asyncio.run(
        execute_transaction_and_update_bid(from_identifier,
                                           to_identifier,
                                           value,
                                           request_strategy,
                                           bid_id,
                                           header))


@router.get("/session/transactions")
def session_transactions(request_strategy: RequestContext = Depends(get_request_strategy),
                         user=Depends(get_current_user),
                         db=Depends(get_db_session)):
    try:
        header = get_header(db=db, user_email=user.email)
        response = request_strategy.make_request(endpoint="/market/session-transactions/",
                                                 method="get",
                                                 headers=header)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=response.json(),
                        status_code=response.status_code,
                        media_type="application/json")
