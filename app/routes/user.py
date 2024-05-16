from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.orm import Session

from app.apis.RequestStrategy import RequestContext
from app.crud import add_token, cleanup_expired_tokens
from app.dependencies import authenticate_user, create_access_token, pwd_context
from app.dependencies import get_db_session, get_request_strategy
from app.models.models import User
from app.routes.wallet import get_payment_processor
from app.schemas.schemas import UserLoginSchema, UserRegistrationSchema
from app.schemas.user.schema import LoginResponseModel, RegisterResponseModel

router = APIRouter()


@router.post("/login", response_model=LoginResponseModel)
async def login(credentials: UserLoginSchema,
                background_tasks: BackgroundTasks,
                request_strategy: RequestContext = Depends(get_request_strategy),
                db: Session = Depends(get_db_session)):

    response = request_strategy.make_request(endpoint="/token",
                                             method="post",
                                             data=credentials.model_dump())

    user = authenticate_user(credentials.email, credentials.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.email})

    if response.status_code == status.HTTP_200_OK:
        # update the token in the database
        logger.debug(f"Adding token to database: {response.json()}")
        add_token(db=db, token=response.json()['access'])
        background_tasks.add_task(cleanup_expired_tokens, db)
        return JSONResponse({"access_token": access_token, "token_type": "bearer"})

    logger.error(f"Failed to login in the remote predico server: {response.json()}")
    raise HTTPException(status_code=response.status_code, detail="Failed to login")


@router.post("/register", response_model=RegisterResponseModel)
def register_user(credentials: UserRegistrationSchema,
                  request_strategy: RequestContext = Depends(get_request_strategy),
                  db: Session = Depends(get_db_session)):

    # noinspection PyTypeChecker
    user = db.query(User).filter(User.email == credentials.email).first()

    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # If user does not exist, proceed with registration logic
    # Here you would hash the password, create a new User object, add to the session, and commit.
    # For example:
    hashed_password = pwd_context.hash(credentials.password)
    new_user = User(email=credentials.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()

    response = request_strategy.make_request(data=credentials.model_dump(),
                                             endpoint="/user/register/",
                                             method="post")

    # Directly return the remote APIs response
    content = response.json()  # Assuming the remote API returns JSON
    status_code = response.status_code

    if status_code == status.HTTP_201_CREATED:

        try:
            # Initialize the wallet only if it's not already initialized
            payment_processor = get_payment_processor()
            payment_processor.create_account(identifier=credentials.email)
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
