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

from src.controller import WalletController


def get_wallet_balances(user_list):

    for user in user_list:
        email = user["email"]
        password = user["password"]
        try:
            # Create wallet & account:
            wallet = WalletController(email=email, password=password).connect()
            balance = wallet.get_balance()
            logger.info(f'User {email} balance is {balance}')
        except Exception:
            logger.exception(f'Failed to retrieve balance for user {email}!')


if __name__ == '__main__':
    # Load users from JSON file:
    with open('files/users.json', 'r') as outfile:
        users = json.load(outfile)
    # Register users:
    get_wallet_balances(users)
