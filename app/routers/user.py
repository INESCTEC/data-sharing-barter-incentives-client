import json

from fastapi import APIRouter, Depends, HTTPException, Response, status
from loguru import logger
from payment.PaymentGateway.IOTAPayment.IOTAPaymentController import IOTAPaymentController
from sqlalchemy.orm import Session

from app.RequestController import RequestController
from app.database import get_db_session
from app.helpers.helper import wallet_config
from app.schemas.schemas import UserLoginSchema, UserRegistrationSchema

router = APIRouter()


@router.post("/login")
def login(credentials: UserLoginSchema, db: Session = Depends(get_db_session)):
    controller = RequestController(db=db)
    response = controller.post('api/token', data=credentials.model_dump(exclude_none=True))
    if response.status_code == 200:
        # update the token in the database
        controller.add_token(db_session=db, token=response.json()['access'])
        return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")
    raise HTTPException(status_code=response.status_code, detail="Failed to login")


@router.post("/register")
def register_wallet(register_schema: UserRegistrationSchema, db: Session = Depends(get_db_session)):

    controller = RequestController(db=db)
    response = controller.post('api/user/register', data=register_schema.model_dump(exclude_none=True))

    # Directly return the remote APIs response
    content = response.json()  # Assuming the remote API returns JSON
    status_code = response.status_code

    if status_code == status.HTTP_201_CREATED:
        try:
            # Initialize the wallet only if it's not already initialized
            payment_controller = IOTAPaymentController(config=wallet_config())
            payment_controller.create_account(identifier=register_schema.email)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            content = {"error": str(e)}
            logger.error(str(e))
        # Request funds from the faucet for each account

    return Response(content=json.dumps(content), status_code=status_code, media_type="application/json")

