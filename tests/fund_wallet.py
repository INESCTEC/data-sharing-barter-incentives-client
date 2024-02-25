import requests
from loguru import logger
from constants import USER_EMAIL_EXAMPLE, BASE_URL


def fund_wallet(start=1, number_of_users=10):
    for i in range(start, number_of_users):
        email = USER_EMAIL_EXAMPLE.format(user=i)
        logger.debug(f"Funding wallet for user: {USER_EMAIL_EXAMPLE.format(user=i)}")
        response = requests.get(f'{BASE_URL}/wallet/request_funds/?email={email}')
        logger.info(response.json())