from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger
from payment.PaymentGateway.IOTAPayment.IOTAPaymentController import IOTAPaymentController
from sqlalchemy.orm import Session

from app.apis.RequestStrategy import RequestContext
from app.crud import add_token
from app.dependencies import get_request_strategy, get_db_session
from app.helpers.helper import wallet_config
from app.schemas.schemas import UserLoginSchema, UserRegistrationSchema

router = APIRouter()


@router.post("/login")
def login(credentials: UserLoginSchema,
          db: Session = Depends(get_db_session),
          request_strategy: RequestContext = Depends(get_request_strategy)):

    response = request_strategy.make_request(endpoint="/token",
                                             method="post",
                                             data=credentials.model_dump())

    if response.status_code == status.HTTP_200_OK:
        # update the token in the database
        logger.debug(f"Adding token to database: {response.json()}")
        add_token(db=db, token=response.json()['access'])
        return JSONResponse(content=response.json(), status_code=200, media_type="application/json")
    logger.error(f"Failed to login: {response.json()}")
    raise HTTPException(status_code=response.status_code, detail="Failed to login")


@router.post("/register")
def register_wallet(credentials: UserRegistrationSchema,
                    request_strategy: RequestContext = Depends(get_request_strategy)):

    response = request_strategy.make_request(data=credentials.model_dump(),
                                             endpoint="/user/register/",
                                             method="post")

    # Directly return the remote APIs response
    content = response.json()  # Assuming the remote API returns JSON
    status_code = response.status_code

    if status_code == status.HTTP_201_CREATED:

        try:
            # Initialize the wallet only if it's not already initialized
            payment_controller = IOTAPaymentController(config=wallet_config())
            payment_controller.create_account(identifier=credentials.email)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            content = {"error": str(e)}
            logger.error(str(e))
            # Request funds from the faucet for each account

        return JSONResponse(content=content,
                            status_code=status_code,
                            media_type="application/json")

    else:
        raise HTTPException(status_code=status_code, detail=content)
