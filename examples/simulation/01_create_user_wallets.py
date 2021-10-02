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
from src.util.mock.user_generators import generate_users


def create_user_wallets(nr_users):
    faucet = FaucetController()
    user_list = generate_users(nr_users=nr_users)
    wallet_user_list = []
    for user in user_list:
        email = user["email"]
        password = user["password"]
        logger.info(f'Creating new wallet: {email}')
        try:
            # Create wallet & account:
            wallet = WalletController(email=email, password=password)
            wallet.create_wallet(store_mnemonic=True)
            wallet.create_account(alias=email)
            # Get address & request tokens from faucet:
            address = wallet.get_address()["address"]["inner"]
            faucet.request_tokens(address=address)
            # Save:
            user["wallet_address"] = address
            wallet_user_list.append(user)
            logger.info(f'Creating new wallet: {email} ... Ok!')
        except Exception:
            logger.exception(f'Creating new wallet: {email} ... Failed!')
    return wallet_user_list


if __name__ == '__main__':
    NR_USERS = 3
    wallet_user_list = create_user_wallets(nr_users=NR_USERS)
    if len(wallet_user_list) > 0:
        # Save users to JSON file:
        with open('files/users.json', 'w') as outfile:
            json.dump(wallet_user_list, outfile, indent="\t")
