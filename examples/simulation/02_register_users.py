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

from src.controller import ClientController


def register_users(user_list):
    # Initialize API controller:
    controller = ClientController()
    registered_users = []
    for user in user_list:
        logger.info(f"Registering user: {user['email']}")
        try:
            # Register user:
            controller.register(
                email=user["email"],
                password=user["password"],
                password_conf=user["password"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                role=user["role"],
            )
            controller.login(
                email=user["email"],
                password=user["password"]
            )
            controller.register_wallet_address(user["wallet_address"])
            registered_users.append(user)
            logger.info(f"Registering user: {user['email']} ... Ok!")
        except Exception:
            logger.exception(f"Registering user: {user['email']} ... Failed!")

    return registered_users


if __name__ == '__main__':

    # Load users from JSON file:
    with open('files/users.json', 'r') as outfile:
        users = json.load(outfile)
    # Register users:
    register_users(users)
