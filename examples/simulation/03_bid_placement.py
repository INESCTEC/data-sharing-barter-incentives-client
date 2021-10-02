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

from src.controller import ClientController, WalletController


def bid_placement(user_list, bid_price, max_payment):
    # Initialize API controller:
    controller = ClientController()

    for user in user_list:
        logger.info(f"Placing bid for user: {user['email']}")
        email = user["email"]
        password = user["password"]
        try:
            # -- login to market REST:
            controller.login(user['email'], user['password'])
            # -- Get market wallet address:
            market_wallet_address = controller.get_market_wallet_address()
            # -- Get current last active session (status='closed'):
            session_data = controller.list_last_session(status='open')
            # Get session_id & fetch data for that session:
            active_session_id = session_data["market_session_id"]
            # --------------
            # -- initialize WALLET controller:
            wallet = WalletController(email=email, password=password).connect()
            node_response = wallet.transfer_tokens(
                amount=max_payment,
                address=market_wallet_address
            )
            tangle_msg_id = node_response['id']
            # -- Place bid & IOTAs transaction confirmation:
            response = controller.place_bid(
                session_id=active_session_id,
                bid_price=bid_price,
                max_payment=max_payment,
                gain_func="mse",
                tangle_msg_id=tangle_msg_id
            )
            logger.info(response)
            logger.info(f"Placing bid for user: {user['email']} ... Ok!")
        except Exception:
            logger.exception(f"Placing bid for user: {user['email']} "
                             f"... Failed!")


if __name__ == '__main__':

    # Load users from JSON file:
    with open('files/users.json', 'r') as outfile:
        users = json.load(outfile)
    # Register users:
    bid_placement(user_list=users, max_payment=2500000, bid_price=500000)
