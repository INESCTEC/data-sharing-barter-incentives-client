"""
Description:
- Creates fictitious users
- Registers users in VALOREM platform
- Creates wallet for each user

Date: 2021-07-01
Author: Ricardo Andrade (jose.r.andrade@inesctec.pt)
"""
import os
import json

from loguru import logger
from dotenv import load_dotenv

__ENV_PATH__ = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(__ENV_PATH__)

from src.controller import WalletController


def transfer_to_firefly(user_list, firefly_address):
    for user in user_list:
        logger.info(f"Transferring user {user['email']} balance to firefly")
        email = user["email"]
        password = user["password"]
        try:
            # -- initialize WALLET controller:
            wallet = WalletController(email=email, password=password).connect()
            balance = wallet.get_balance()["available"]
            node_response = wallet.transfer_tokens(
                amount=balance,
                address=firefly_address
            )
            logger.info(node_response)
        except Exception:
            logger.exception(f"Placing bid for user: {user['email']} "
                             f"... Failed!")


if __name__ == '__main__':
    FIREFLY_ADDRESS = "atoi1qp5h5gr582d5jtkv46v9dac5r7v9gev2d84mpz4ss2eq2suaqq4gk8wacmp"
    # Load users from JSON file:
    with open('files/users.json', 'r') as outfile:
        users = json.load(outfile)
    # Register users:
    transfer_to_firefly(user_list=users,
                        firefly_address=FIREFLY_ADDRESS)
