import requests
from loguru import logger
from constants import BASE_URL, PASSWORD


def login(email):
    data = {
        "email": email,
        "password": PASSWORD
    }
    logger.debug(f"Logging in user: {email}")
    response = requests.post(f'{BASE_URL}/user/login', json=data)
    logger.info(response.json())


