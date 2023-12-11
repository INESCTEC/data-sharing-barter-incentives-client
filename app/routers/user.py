from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.schemas import UserRegistrationSchema
from src.controller.exception.APIException import RegisterException
from src.AgentManager import AgentManager

router = APIRouter()

ag = AgentManager()
ag.load_available_users()


@router.post("/register_user/")
def register_user(user: UserRegistrationSchema):
    """
    This endpoint registers a list of users in the market.
    It creates a wallet and an account for each user and returns the wallet address
    to be registered in the market.
    """
    try:
        ag.create_user_wallet(user=user)
    except Exception as e:
        return JSONResponse(content={"message": f"Error creating user wallets: {str(e)}"}, status_code=400)

    try:
        ag.register_user(user=user)
        return JSONResponse(
            content={"message": "User registered successfully. "
                                "Please verify user email to validate the registration."},
            status_code=200)
    except RegisterException as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
