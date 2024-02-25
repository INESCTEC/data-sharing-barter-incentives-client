import requests
from loguru import logger
from app.schemas.schemas import UserRegistrationSchema
from constants import BASE_URL, USER_EMAIL_EXAMPLE, PASSWORD


def register_user(number_of_users=10):
    user_first_name = 'test-user-{user}-first-name'
    user_last_name = 'test-user-{user}-last-name'
    for i in range(1, number_of_users):
        data = UserRegistrationSchema(
            email=USER_EMAIL_EXAMPLE.format(user=i),
            password=PASSWORD,
            password_conf=PASSWORD,
            first_name=user_first_name.format(user=i),
            last_name=user_last_name.format(user=i),
            role=["buyer", "seller"],
        )
        logger.debug(f"Registering user: {USER_EMAIL_EXAMPLE.format(user=i)}")
        response = requests.post(f'{BASE_URL}/user/register', json=data.model_dump())
        logger.info(response.json())