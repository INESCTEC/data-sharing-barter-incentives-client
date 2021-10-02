# -- For debug purposes. Not necessary when using docker containers
from dotenv import load_dotenv
load_dotenv(".env")

import os
import click

from loguru import logger

from src.controller import ClientController, WalletController

VALOREM_WALLET_ADDRESS = os.environ["VALOREM_WALLET_ADDRESS"]

# -- Init Logger(s):
logs_dir = os.path.join("files", "logs")
logger.add(os.path.join(logs_dir, "info.log"),
           format="{time:YYYY-MM-DD HH:mm:ss} | {level:<5} | {message}",
           rotation="1 day",
           level='INFO',
           compression="zip",
           backtrace=True)
logger.info("-" * 70)
logger.info("-" * 70)


@click.command()
@click.option('--email',
              help='User email.',
              required=True,
              type=str)
@click.option('--password',
              help='User password.',
              required=True,
              type=str)
@click.option('--first_name',
              help='User first name.',
              required=True,
              type=str)
@click.option('--last_name',
              help='User last name.',
              required=True,
              type=str)
@click.option('--role',
              help='User role.',
              required=True,
              type=click.Choice(['buyer', 'seller'], case_sensitive=True))
def register(email, password, first_name, last_name, role):
    # Creates user wallet if does not exist:
    logger.info(f'Creating new wallet: {email}')
    try:
        wallet = WalletController(email=email)
        wallet.create_wallet(store_mnemonic=True)
        wallet.create_account(alias=email)
    except ValueError:
        logger.info(f'Creating new wallet: {email} ... Failed! Already exists')

    # Registers user in VALOREM API:
    role_dict = {"buyer": [1, 2], "seller": [2]}
    logger.info(f'Registering user: {email}')
    controller = ClientController()
    controller.register(
        email=email,
        password=password,
        password_conf=password,
        first_name=first_name,
        last_name=last_name,
        role=role_dict[role]
    )


@click.command()
@click.option('--email',
              help='User email.',
              required=True,
              type=str)
@click.option('--password',
              help='User password.',
              required=True,
              type=str)
@click.option('--bid_price',
              help='Market bid price (MIOTA).',
              required=True,
              type=int)
@click.option('--max_payment',
              help='Market max payment price (MIOTA).',
              required=True,
              type=int)
@click.option('--gain_func',
              help='User last name.',
              required=False,
              default='mse',
              type=str)
@logger.catch()
def place_bid(email, password, bid_price, max_payment, gain_func):
    # -- initialize REST controller
    controller = ClientController()
    print(email, password)

    # -- initialize WALLET controller:
    wallet = WalletController(email=email).connect()
    self_wallet_address = wallet.get_address()["address"]["inner"]

    # -- login to market REST:
    controller.login(email, password)
    logger.info(f'Placing bid for user: {email}')

    # -- Get current last active session (status='closed'):
    session_data = controller.list_last_session(status='open')
    # Get session_id & fetch data for that session:
    active_session_id = session_data["market_session_id"]

    # -- Transfer 'max_payment' & Get transaction ID (proof-of-payment)
    market_wallet_address = VALOREM_WALLET_ADDRESS
    node_response = wallet.transfer_tokens(amount=max_payment,
                                           address=market_wallet_address)
    tangle_msg_id = node_response['id']
    # -- Place bid & IOTAs transaction confirmation:
    response = controller.place_bid(
        session_id=active_session_id,
        bid_price=bid_price,
        max_payment=max_payment,
        gain_func=gain_func,
        tangle_msg_id=tangle_msg_id
    )
    logger.info(response)


@click.command()
@click.option('--email',
              help='User email.',
              required=True,
              type=str)
@click.option('--password',
              help='User password.',
              required=True,
              type=str)
def get_forecasts(email, password):
    # initialize REST controller
    controller = ClientController()
    # login to market REST:
    controller.login(email, password)
    # Bid placement:
    # todo: fetch forecasts from VALOREM REST and store it on user DB


@click.group()
@logger.catch
def cli():
    pass


cli.add_command(register)
cli.add_command(place_bid)
cli.add_command(get_forecasts)


if __name__ == '__main__':
    cli()
