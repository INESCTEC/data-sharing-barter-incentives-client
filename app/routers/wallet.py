from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import EmailStr

from src.AgentManager import AgentManager
from src.controller.exception.APIException import RegisterWalletException

router = APIRouter()

ag = AgentManager()
ag.load_available_users()


@router.get("/get_wallet_balance/")
def get_balance():
    ag.load_available_users()
    return {"balance": ag.get_wallet_balances()}


@router.get("/register_wallet/")
def register_wallet(email: EmailStr):
    ag.load_available_users()
    user = ag.get_user_by_email(email)
    if not user:
        return JSONResponse({"message": "User not found."}, status_code=404)
    try:
        ag.login(user=user)
        response = ag.register_wallet(user=user, address=user['address'])
    except RegisterWalletException as e:
        if e.errors:
            return JSONResponse({"message": e.errors}, status_code=400)
        return JSONResponse({"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=400)

    return JSONResponse({"message": response}, status_code=200)


@router.get("/fund_wallet/")
def fund_wallet(email: EmailStr):
    """
    This endpoint funds the wallet of a provided user with 10000 tokens.
    """
    ag.load_available_users()
    user = ag.get_user_by_email(email)
    if not user:
        return JSONResponse({"message": "User not found."}, status_code=404)
    ag.request_tokens(user=user)
    return JSONResponse({"message": "Wallet funded."}, status_code=200)