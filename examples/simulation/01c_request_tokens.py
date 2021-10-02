"""
Description:
- Creates fictitious users
- Creates wallet for each user
- Requests tokens for each user from IOTA faucet

Date: 2021-09-30
Author: Ricardo Andrade (jose.r.andrade@inesctec.pt)
"""
import os
import json

from loguru import logger
from dotenv import load_dotenv

__ENV_PATH__ = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(__ENV_PATH__)

from src.controller import WalletController, FaucetController


def request_tokens(user_list):
    faucet = FaucetController()
    for user in user_list:
        email = user["email"]
        password = user["password"]
        logger.info(f'Requesting tokens for user: {email}')
        try:
            # Create wallet & account:
            wallet = WalletController(email=email, password=password).connect()
            # Get address & request tokens from faucet:
            address = wallet.get_address()["address"]["inner"]
            faucet.request_tokens(address=address)
            logger.info(f'Requesting tokens for user: {email} ... Ok!')
        except Exception:
            logger.exception(f'Failed to request tokens for user {email}!')


if __name__ == '__main__':
    # Load users from JSON file:
    with open('files/users.json', 'r') as outfile:
        users = json.load(outfile)
    # Register users:
    request_tokens(users)
