from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.schemas import UserRegistrationSchema, BidSchema
from pydantic import EmailStr
from src.AgentManager import AgentManager
from src.BiddingService import BiddingService, BidException, ExistingBidException
from fastapi import BackgroundTasks
from loguru import logger


router = APIRouter()

ag = AgentManager()
ag.load_available_users()


@router.get("/open/")
def open_session(email: EmailStr):

    user = ag.get_user_by_email(email)
    ag.login(user=user)
    if not user:
        return JSONResponse({"message": "User not found."}, status_code=404)
    bidding_service = BiddingService()
    try:
        response = bidding_service.list_open_session(user=user)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)

    return JSONResponse({"message": response}, status_code=200)


@router.patch("/bid/")
def patch_bid(email, bid_id, tangle_msg_id):

    ag.load_available_users()
    user = ag.get_user_by_email(email)
    bidding = BiddingService()
    bid = {"bid_id": bid_id, "tangle_msg_id": tangle_msg_id}
    bidding.patch_bid(user=user, bid=bid)
    return JSONResponse({"message": "Bid patched."}, status_code=200)


@router.post("/bid/")
def bid_session(bid: BidSchema, background_tasks: BackgroundTasks):

    ag.load_available_users()
    user = ag.get_user_by_email(bid.email)
    if not user:
        return JSONResponse({"message": "User not found."}, status_code=404)
    if 'registered_wallet' not in user:
        return JSONResponse({"message": "User has no registered wallet."}, status_code=400)
    if 'resources' not in user:
        return JSONResponse({"message": "User has no resources."}, status_code=400)
    for resource in user['resources']:
        if resource['id'] == bid.resource:
            break
    else:
        return JSONResponse({"message": "Resource not found."}, status_code=400)

    bidding_service = BiddingService()
    session = ag.list_current_open_session(user=user)

    if not session:
        return JSONResponse({"message": "There is no open session."}, status_code=404)

    try:
        response = bidding_service.place_bid(
            user=user,
            max_payment=bid.max_payment,
            session_id=session["id"],
            bid_price=bid.price,
            resource=bid.resource)

        logger.info(f"Response: {response}")
        background_tasks.add_task(async_patch_operation, user, response)

    except BidException as e:
        return JSONResponse({"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)

    return JSONResponse({"message": response}, status_code=200)


def async_patch_operation(user, bid):

    bidding_service = BiddingService()
    bidding_service.patch_bid(user, bid)


@router.get("/bid/")
def list_bid(email: EmailStr):

    ag.load_available_users()
    user = ag.get_user_by_email(email)

    response = ag.list_market_bids(user=user)
    return JSONResponse({"bids": response})